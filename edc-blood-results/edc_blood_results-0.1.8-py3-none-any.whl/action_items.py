from django.apps import apps as django_apps
from django.conf import settings
from edc_action_item import Action, site_action_items
from edc_adverse_event.constants import AE_INITIAL_ACTION
from edc_constants.constants import HIGH_PRIORITY, YES
from edc_visit_schedule.utils import is_baseline

from .constants import (
    BLOOD_RESULTS_EGFR_ACTION,
    BLOOD_RESULTS_FBC_ACTION,
    BLOOD_RESULTS_GLU_ACTION,
    BLOOD_RESULTS_HBA1C_ACTION,
    BLOOD_RESULTS_INSULIN_ACTION,
    BLOOD_RESULTS_LFT_ACTION,
    BLOOD_RESULTS_LIPID_ACTION,
    BLOOD_RESULTS_RFT_ACTION,
)

subject_app_label = getattr(
    settings, "EDC_BLOOD_RESULTS_MODEL_APP_LABEL", settings.SUBJECT_APP_LABEL
)


class BaseBloodResultsAction(Action):
    name = None
    display_name = None
    reference_model = None

    priority = HIGH_PRIORITY
    show_on_dashboard = True
    create_by_user = False

    def reopen_action_item_on_change(self):
        return False

    def get_next_actions(self):
        next_actions = []
        if (
            self.reference_obj.results_abnormal == YES
            and self.reference_obj.results_reportable == YES
            and not is_baseline(self.reference_obj.subject_visit)
        ):
            # AE for reportable result, though not on DAY1.0
            next_actions = [AE_INITIAL_ACTION]
        return next_actions


class BloodResultsLftAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_LFT_ACTION
    display_name = "Reportable result: LFT"
    reference_model = f"{subject_app_label}.bloodresultslft"


class BloodResultsRftAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_RFT_ACTION
    display_name = "Reportable result: RFT"
    reference_model = f"{subject_app_label}.bloodresultsrft"


class BloodResultsFbcAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_FBC_ACTION
    display_name = "Reportable result: FBC"
    reference_model = f"{subject_app_label}.bloodresultsfbc"


class BloodResultsLipidAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_LIPID_ACTION
    display_name = "Reportable result: LIPIDS"
    reference_model = f"{subject_app_label}.bloodresultslipid"


class BloodResultsEgfrAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_EGFR_ACTION
    display_name = "Reportable eGFR"
    reference_model = f"{subject_app_label}.bloodresultsfbc"


class BloodResultsGluAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_GLU_ACTION
    display_name = "Reportable Blood Glucose"
    reference_model = f"{subject_app_label}.bloodresultsglu"


class BloodResultsHba1cAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_HBA1C_ACTION
    display_name = "Reportable HbA1c"
    reference_model = f"{subject_app_label}.bloodresultshba1c"


class BloodResultsInsulinAction(BaseBloodResultsAction):
    name = BLOOD_RESULTS_INSULIN_ACTION
    display_name = "Reportable Insulin"
    reference_model = f"{subject_app_label}.bloodresultsins"


def register_actions():
    for action_item in [
        BloodResultsEgfrAction,
        BloodResultsFbcAction,
        BloodResultsGluAction,
        BloodResultsHba1cAction,
        BloodResultsInsulinAction,
        BloodResultsLftAction,
        BloodResultsLipidAction,
        BloodResultsRftAction,
    ]:

        try:
            django_apps.get_model(action_item.reference_model)
        except LookupError as e:
            pass
        else:
            site_action_items.register(action_item)


register_actions()
