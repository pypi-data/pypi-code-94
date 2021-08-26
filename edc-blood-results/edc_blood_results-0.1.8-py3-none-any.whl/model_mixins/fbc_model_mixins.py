from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_reportable import GRAMS_PER_DECILITER, PERCENT
from edc_reportable.units import (
    CELLS_PER_MILLIMETER_CUBED,
    CELLS_PER_MILLIMETER_CUBED_DISPLAY,
    FEMTOLITERS_PER_CELL,
    PICOGRAMS_PER_CELL,
    TEN_X_9_PER_LITER,
)

from .factory import blood_results_model_mixin_factory


class HaemoglobinModelMixin(
    blood_results_model_mixin_factory(
        utest_id="haemoglobin",
        verbose_name="Haemoglobin",
        units_choices=((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),),
        decimal_places=1,
    ),
    models.Model,
):
    class Meta:
        abstract = True


class HctModelMixin(
    blood_results_model_mixin_factory(
        utest_id="hct",
        verbose_name="Hematocrit",
        units_choices=((PERCENT, PERCENT),),
        validators=[MinValueValidator(1.0), MaxValueValidator(999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class MchModelMixin(
    blood_results_model_mixin_factory(
        utest_id="mch",
        units_choices=((PICOGRAMS_PER_CELL, PICOGRAMS_PER_CELL),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class MchcModelMixin(
    blood_results_model_mixin_factory(
        utest_id="mchc",
        units_choices=((GRAMS_PER_DECILITER, GRAMS_PER_DECILITER),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class McvModelMixin(
    blood_results_model_mixin_factory(
        utest_id="mcv",
        units_choices=((FEMTOLITERS_PER_CELL, FEMTOLITERS_PER_CELL),),
    ),
    models.Model,
):
    class Meta:
        abstract = True


class PlateletsModelMixin(
    blood_results_model_mixin_factory(
        utest_id="platelets",
        verbose_name="Platelets",
        units_choices=(
            (TEN_X_9_PER_LITER, TEN_X_9_PER_LITER),
            (CELLS_PER_MILLIMETER_CUBED, CELLS_PER_MILLIMETER_CUBED_DISPLAY),
        ),
        decimal_places=0,
        validators=[MinValueValidator(1.0), MaxValueValidator(9999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class RbcModelMixin(
    blood_results_model_mixin_factory(
        utest_id="rbc",
        verbose_name="Red blood cell count",
        units_choices=(
            (TEN_X_9_PER_LITER, TEN_X_9_PER_LITER),
            (CELLS_PER_MILLIMETER_CUBED, CELLS_PER_MILLIMETER_CUBED),
        ),
        validators=[MinValueValidator(1.0), MaxValueValidator(999999.0)],
    ),
    models.Model,
):
    class Meta:
        abstract = True


class WbcModelMixin(
    blood_results_model_mixin_factory(
        utest_id="wbc",
        units_choices=(
            (TEN_X_9_PER_LITER, TEN_X_9_PER_LITER),
            (CELLS_PER_MILLIMETER_CUBED, CELLS_PER_MILLIMETER_CUBED_DISPLAY),
        ),
    ),
    models.Model,
):
    class Meta:
        abstract = True
