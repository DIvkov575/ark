import logging
import io
import os
import tempfile

import numpy as np
import pydicom
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F

import onconet.transformers.factory as transformer_factory
from models.base import BaseModel, ArgsDict
from onconet.models.mirai_full import MiraiModel
from models.utils import dicom_to_image_dcmtk, dicom_to_arr
from onconet.transformers.basic import ComposeTrans
from onconet.utils import parsing

logger = logging.getLogger('ark')


class DensityModel(BaseModel):
    def __init__(self, args):
        super().__init__()
        self.args = args
        self.required_data = None
        self.model = self.load_model()
        self.__version__ = "0.1a"

    @staticmethod
    def download_if_needed(args, cache_dir='~/.mirai'):
        cache_dir = os.path.expanduser(cache_dir)
        args.snapshot = os.path.expanduser(args.snapshot)
        MiraiModel.download_if_needed(args, cache_dir)

    def load_model(self):
        logger.info("Loading model...")
        self.args.cuda = self.args.cuda and torch.cuda.is_available()

        self.download_if_needed(self.args)
        model_path = os.path.expanduser(self.args.snapshot)
        model = torch.load(model_path, map_location='cpu')

        # Unpack models that were trained as data parallel
        if isinstance(model, nn.DataParallel):
            model = model.module

        # Version mismatch workaround
        model._model.args.survival_analysis_setup = self.args.survival_analysis_setup
        model._model.args.pred_risk_factors = self.args.pred_risk_factors

        # Add use precomputed hiddens for models trained before it was introduced.
        # Assumes a resnet WHybase backbone
        try:
            model._model.args.use_precomputed_hiddens = self.args.use_precomputed_hiddens
            model._model.args.cuda = self.args.cuda
        except Exception as e:
            logger.debug("Exception caught, skipping precomputed hiddens")
            pass

        return model

    def label_map(self, pred):
        pred = pred.argmax()
        density_labels = [1, 2, 3, 4]
        return density_labels[pred]

    def process_image(self, image, model, risk_factor_vector=None):
        logger.info("Processing image...")

        test_image_transformers = parsing.parse_transformers(self.args.test_image_transformers)
        test_tensor_transformers = parsing.parse_transformers(self.args.test_tensor_transformers)
        test_transformers = transformer_factory.get_transformers(test_image_transformers, test_tensor_transformers, self.args)
        transforms = ComposeTrans(test_transformers)

        ## Apply transformers
        x = transforms(image, self.args.additional)
        x = autograd.Variable(x.unsqueeze(0))
        risk_factors = autograd.Variable(risk_factor_vector.unsqueeze(0)) if risk_factor_vector is not None else None
        logger.debug("Image size: {}".format(x.size()))

        if self.args.cuda:
            x = x.cuda()
            model = model.cuda()

            if risk_factor_vector is not None:
                risk_factors = risk_factors.cuda()

            logger.debug("Inference with GPU")
        else:
            model = model.cpu()
            logger.debug("Inference with CPU")

        model_output = model(x, risk_factors)
        prediction_logits = model_output[0]
        # Index 0 to toss batch dimension
        pred_y = F.softmax(prediction_logits, dim=-1)[0]
        pred_y = np.array(self.label_map(pred_y.cpu().data.numpy()))

        logger.info("Pred: {}".format(pred_y))

        return pred_y

    def run_model(self, dicom_files, payload=None, to_dict=False, return_attentions=False):

        logger = logging.getLogger('ark')
        logger.info(f"Beginning inference with density model version {self.__version__}")
        if isinstance(dicom_files[0], bytes):
            dicom_files = [io.BytesIO(dicom_file) for dicom_file in dicom_files]
        for ff in dicom_files:
            ff.seek(0)
        report = self._run_model(dicom_files, payload=payload)

        return report

    def _run_model(self, dicom_files, payload=None, **kwargs):
        if payload is None:
            payload = {'dcmtk': False}
        elif 'dcmtk' not in payload:
            payload['dcmtk'] = False

        use_dcmtk = payload.get('dcmtk', False)
        preds = []

        for dicom in dicom_files:
            dicom.seek(0)
            if use_dcmtk:
                logger.debug(f"Using dcmtk")
                dicom_tmp_file = tempfile.NamedTemporaryFile(suffix='.dcm')
                image_tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
                dicom_path = dicom_tmp_file.name
                image_path = image_tmp_file.name
                logger.debug("Temp DICOM path: {}".format(dicom_path))
                logger.debug("Temp image path: {}".format(image_path))

                dicom_tmp_file.write(dicom.read())

                image = dicom_to_image_dcmtk(dicom_path, image_path)
                logger.debug('Image mode: {}'.format(image.mode))
            else:
                logger.debug(f"Using pydicom")
                dicom_obj = pydicom.dcmread(dicom)
                image = dicom_to_arr(dicom_obj, pillow=True)

            risk_factor_vector = None
            preds.append(self.process_image(image, self.model, risk_factor_vector))

        counts = np.bincount(preds)
        y = np.argmax(counts)

        if isinstance(y, np.generic):
            y = y.item()

        report = {'predictions': y}

        return report
