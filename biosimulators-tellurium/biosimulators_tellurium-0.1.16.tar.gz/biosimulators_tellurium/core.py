""" Methods for using tellurium to execute SED tasks in COMBINE/OMEX archives and save their outputs

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-01-04
:Copyright: 2020-2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from .config import Config
from .data_model import SedmlInterpreter, KISAO_ALGORITHM_MAP
from biosimulators_utils.combine.exec import exec_sedml_docs_in_archive
from biosimulators_utils.config import get_config as get_biosimulators_config
from biosimulators_utils.log.data_model import Status, CombineArchiveLog, SedDocumentLog, StandardOutputErrorCapturerLevel, TaskLog  # noqa: F401
from biosimulators_utils.log.utils import init_sed_document_log, StandardOutputErrorCapturer
from biosimulators_utils.viz.data_model import VizFormat  # noqa: F401
from biosimulators_utils.report.data_model import DataSetResults, ReportResults, ReportFormat, SedDocumentResults, VariableResults  # noqa: F401
from biosimulators_utils.report.io import ReportWriter
from biosimulators_utils.sedml import exec as sedml_exec
from biosimulators_utils.sedml import validation
from biosimulators_utils.sedml.data_model import (
    Task, ModelLanguage, SteadyStateSimulation, UniformTimeCourseSimulation,
    Symbol, Report, DataSet, Plot2D, Curve, Plot3D, Surface)
from biosimulators_utils.sedml.io import SedmlSimulationReader, SedmlSimulationWriter
from biosimulators_utils.simulator.utils import get_algorithm_substitution_policy
from biosimulators_utils.utils.core import raise_errors_warnings, validate_str_value, parse_value
from biosimulators_utils.warnings import warn, BioSimulatorsWarning
from kisao.data_model import AlgorithmSubstitutionPolicy, ALGORITHM_SUBSTITUTION_POLICY_LEVELS
from kisao.utils import get_preferred_substitute_algorithm_by_ids
from tellurium.sedml.tesedml import SEDMLCodeFactory
import datetime
import functools
import glob
import numpy
import os
import pandas
import shutil
import tellurium
import tempfile
import tellurium.sedml.tesedml
import roadrunner


__all__ = [
    'exec_sedml_docs_in_combine_archive',
    'exec_sed_doc',
    'exec_sed_task',
]


def exec_sedml_docs_in_combine_archive(archive_filename, out_dir,
                                       sedml_interpreter=None,
                                       return_results=False,
                                       report_formats=None, plot_formats=None,
                                       bundle_outputs=None, keep_individual_outputs=None,
                                       raise_exceptions=True):
    """ Execute the SED tasks defined in a COMBINE/OMEX archive and save the outputs

    Args:
        archive_filename (:obj:`str`): path to COMBINE/OMEX archive
        out_dir (:obj:`str`): path to store the outputs of the archive

            * CSV: directory in which to save outputs to files
              ``{ out_dir }/{ relative-path-to-SED-ML-file-within-archive }/{ report.id }.csv``
            * HDF5: directory in which to save a single HDF5 file (``{ out_dir }/reports.h5``),
              with reports at keys ``{ relative-path-to-SED-ML-file-within-archive }/{ report.id }`` within the HDF5 file

        sedml_interpreter (:obj:`SedmlInterpreter`, optional): SED-ML interpreter
        return_results (:obj:`bool`, optional): whether to return the result of each output of each SED-ML file
        report_formats (:obj:`list` of :obj:`ReportFormat`, optional): report format (e.g., csv or h5)
        plot_formats (:obj:`list` of :obj:`VizFormat`, optional): report format (e.g., pdf)
        bundle_outputs (:obj:`bool`, optional): if :obj:`True`, bundle outputs into archives for reports and plots
        keep_individual_outputs (:obj:`bool`, optional): if :obj:`True`, keep individual output files
        raise_exceptions (:obj:`bool`, optional): whether to raise exceptions

    Returns:
        :obj:`tuple`:

            * :obj:`SedDocumentResults`: results
            * :obj:`CombineArchiveLog`: log
    """
    if sedml_interpreter is None:
        sedml_interpreter = Config().sedml_interpreter

    return exec_sedml_docs_in_archive(
        functools.partial(exec_sed_doc, sedml_interpreter=sedml_interpreter),
        archive_filename, out_dir,
        apply_xml_model_changes=sedml_interpreter == SedmlInterpreter.biosimulators,
        return_results=return_results,
        sed_doc_executer_supported_features=(Task, Report, DataSet, Plot2D, Curve, Plot3D, Surface),
        report_formats=report_formats,
        plot_formats=plot_formats,
        bundle_outputs=bundle_outputs,
        keep_individual_outputs=keep_individual_outputs,
        sed_doc_executer_logged_features=(Report, Plot2D, Plot3D),
        raise_exceptions=raise_exceptions,
    )


def exec_sed_doc(doc, working_dir, base_out_path, rel_out_path=None,
                 sedml_interpreter=None,
                 apply_xml_model_changes=False, return_results=False, report_formats=None, plot_formats=None,
                 log=None, indent=0, pretty_print_modified_xml_models=False,
                 log_level=StandardOutputErrorCapturerLevel.c):
    """ Execute the tasks specified in a SED document and generate the specified outputs

    Args:
        doc (:obj:`SedDocument` or :obj:`str`): SED document or a path to SED-ML file which defines a SED document
        working_dir (:obj:`str`): working directory of the SED document (path relative to which models are located)

        base_out_path (:obj:`str`): path to store the outputs

            * CSV: directory in which to save outputs to files
              ``{base_out_path}/{rel_out_path}/{report.id}.csv``
            * HDF5: directory in which to save a single HDF5 file (``{base_out_path}/reports.h5``),
              with reports at keys ``{rel_out_path}/{report.id}`` within the HDF5 file

        rel_out_path (:obj:`str`, optional): path relative to :obj:`base_out_path` to store the outputs
        sedml_interpreter (:obj:`SedmlInterpreter`, optional): SED-ML interpreter
        apply_xml_model_changes (:obj:`bool`, optional): if :obj:`True`, apply any model changes specified in the SED-ML file before
            calling :obj:`task_executer`.
        return_results (:obj:`bool`, optional): whether to return a data structure with the result of each output of each SED-ML
            file
        report_formats (:obj:`list` of :obj:`ReportFormat`, optional): report format (e.g., csv or h5)
        plot_formats (:obj:`list` of :obj:`VizFormat`, optional): plot format (e.g., pdf)
        log (:obj:`SedDocumentLog`, optional): log of the document
        indent (:obj:`int`, optional): degree to indent status messages
        pretty_print_modified_xml_models (:obj:`bool`, optional): if :obj:`True`, pretty print modified XML models
        log_level (:obj:`StandardOutputErrorCapturerLevel`, optional): level at which to log output

    Returns:
        :obj:`tuple`:

            * :obj:`ReportResults`: results of each report
            * :obj:`SedDocumentLog`: log of the document
    """
    if sedml_interpreter is None:
        sedml_interpreter = Config().sedml_interpreter

    if sedml_interpreter == SedmlInterpreter.biosimulators:
        return exec_sed_doc_with_biosimulators(
            doc, working_dir, base_out_path,
            rel_out_path=rel_out_path,
            apply_xml_model_changes=apply_xml_model_changes,
            return_results=return_results,
            report_formats=report_formats,
            plot_formats=plot_formats,
            log=log,
            indent=indent,
            log_level=log_level)

    elif sedml_interpreter == SedmlInterpreter.tellurium:
        return exec_sed_doc_with_tellurium(
            doc, working_dir, base_out_path,
            rel_out_path=rel_out_path,
            apply_xml_model_changes=apply_xml_model_changes,
            return_results=return_results,
            report_formats=report_formats,
            plot_formats=plot_formats,
            log=log,
            indent=indent,
            log_level=log_level)

    else:
        raise NotImplementedError('`{}` is not a supported SED-ML interpreter.'.format(sedml_interpreter))


def exec_sed_doc_with_biosimulators(doc, working_dir, base_out_path, rel_out_path=None,
                                    apply_xml_model_changes=False, return_results=False, report_formats=None, plot_formats=None,
                                    log=None, indent=0, pretty_print_modified_xml_models=False,
                                    log_level=StandardOutputErrorCapturerLevel.c):
    """ Execute the tasks specified in a SED document and generate the specified outputs

    Args:
        doc (:obj:`SedDocument` or :obj:`str`): SED document or a path to SED-ML file which defines a SED document
        working_dir (:obj:`str`): working directory of the SED document (path relative to which models are located)
        base_out_path (:obj:`str`): path to store the outputs

            * CSV: directory in which to save outputs to files
              ``{base_out_path}/{rel_out_path}/{report.id}.csv``
            * HDF5: directory in which to save a single HDF5 file (``{base_out_path}/reports.h5``),
              with reports at keys ``{rel_out_path}/{report.id}`` within the HDF5 file

        rel_out_path (:obj:`str`, optional): path relative to :obj:`base_out_path` to store the outputs
        apply_xml_model_changes (:obj:`bool`, optional): if :obj:`True`, apply any model changes specified in the SED-ML file before
            calling :obj:`task_executer`.
        return_results (:obj:`bool`, optional): whether to return a data structure with the result of each output of each SED-ML
            file
        report_formats (:obj:`list` of :obj:`ReportFormat`, optional): report format (e.g., csv or h5)
        plot_formats (:obj:`list` of :obj:`VizFormat`, optional): plot format (e.g., pdf)
        log (:obj:`SedDocumentLog`, optional): log of the document
        indent (:obj:`int`, optional): degree to indent status messages
        pretty_print_modified_xml_models (:obj:`bool`, optional): if :obj:`True`, pretty print modified XML models
        log_level (:obj:`StandardOutputErrorCapturerLevel`, optional): level at which to log output

    Returns:
        :obj:`tuple`:

            * :obj:`ReportResults`: results of each report
            * :obj:`SedDocumentLog`: log of the document
    """
    sed_task_executer = functools.partial(exec_sed_task, sedml_interpreter=SedmlInterpreter.biosimulators)
    return sedml_exec.exec_sed_doc(sed_task_executer, doc, working_dir, base_out_path,
                                   rel_out_path=rel_out_path,
                                   apply_xml_model_changes=True,
                                   return_results=return_results,
                                   report_formats=report_formats,
                                   plot_formats=plot_formats,
                                   log_level=log_level)


def exec_sed_task(task, variables, log=None, sedml_interpreter=None):
    ''' Execute a task and save its results

    Args:
       task (:obj:`Task`): task
       variables (:obj:`list` of :obj:`Variable`): variables that should be recorded
       log (:obj:`TaskLog`, optional): log for the task
       sedml_interpreter (:obj:`SedmlInterpreter`, optional): SED-ML interpreter

    Returns:
        :obj:`tuple`:

            :obj:`VariableResults`: results of variables
            :obj:`TaskLog`: log

    Raises:
        :obj:`ValueError`: if the task or an aspect of the task is not valid, or the requested output variables
            could not be recorded
        :obj:`NotImplementedError`: if the task is not of a supported type or involves an unsuported feature
    '''

    if sedml_interpreter is None:
        sedml_interpreter = Config().sedml_interpreter

    if sedml_interpreter != SedmlInterpreter.biosimulators:
        raise NotImplementedError('`{}` is not a supported SED-ML interpreter.'.format(sedml_interpreter))

    biosimulators_config = get_biosimulators_config()

    log = log or TaskLog()

    model = task.model
    sim = task.simulation

    if biosimulators_config.VALIDATE_SEDML:
        raise_errors_warnings(validation.validate_task(task),
                              error_summary='Task `{}` is invalid.'.format(task.id))
        raise_errors_warnings(validation.validate_model_language(model.language, ModelLanguage.SBML),
                              error_summary='Language for model `{}` is not supported.'.format(model.id))
        raise_errors_warnings(validation.validate_model_change_types(model.changes, ()),
                              error_summary='Changes for model `{}` are not supported.'.format(model.id))
        raise_errors_warnings(*validation.validate_model_changes(task.model),
                              error_summary='Changes for model `{}` are invalid.'.format(model.id))
        raise_errors_warnings(validation.validate_simulation_type(sim, (SteadyStateSimulation, UniformTimeCourseSimulation)),
                              error_summary='{} `{}` is not supported.'.format(sim.__class__.__name__, sim.id))
        raise_errors_warnings(*validation.validate_simulation(sim),
                              error_summary='Simulation `{}` is invalid.'.format(sim.id))
        raise_errors_warnings(*validation.validate_data_generator_variables(variables),
                              error_summary='Data generator variables for task `{}` are invalid.'.format(task.id))
    target_x_paths_to_sbml_ids = validation.validate_variable_xpaths(variables, model.source, attr='id')

    if biosimulators_config.VALIDATE_SEDML_MODELS:
        raise_errors_warnings(*validation.validate_model(model, [], working_dir='.'),
                              error_summary='Model `{}` is invalid.'.format(model.id),
                              warning_summary='Model `{}` may be invalid.'.format(model.id))

    # read model
    rr = roadrunner.RoadRunner()
    rr.load(model.source)

    # get algorithm to execute
    algorithm_substitution_policy = get_algorithm_substitution_policy()
    exec_alg_kisao_id = get_preferred_substitute_algorithm_by_ids(
        sim.algorithm.kisao_id, KISAO_ALGORITHM_MAP.keys(),
        substitution_policy=algorithm_substitution_policy)
    alg_props = KISAO_ALGORITHM_MAP[exec_alg_kisao_id]

    if alg_props['id'] == 'nleq2':
        integrator = rr.getSteadyStateSolver()
        raise_errors_warnings(validation.validate_simulation_type(sim, (SteadyStateSimulation,)),
                              error_summary='{} `{}` is not supported.'.format(sim.__class__.__name__, sim.id))

    else:
        rr.setIntegrator(alg_props['id'])
        integrator = rr.getIntegrator()
        raise_errors_warnings(validation.validate_simulation_type(sim, (UniformTimeCourseSimulation,)),
                              error_summary='{} `{}` is not supported.'.format(sim.__class__.__name__, sim.id))

    # set the parameters of the integrator
    if exec_alg_kisao_id == sim.algorithm.kisao_id:
        for change in sim.algorithm.changes:
            param_props = alg_props['parameters'].get(change.kisao_id, None)
            if param_props:
                if validate_str_value(change.new_value, param_props['type']):
                    new_value = parse_value(change.new_value, param_props['type'])
                    setattr(integrator, param_props['id'], new_value)

                else:
                    if (
                        ALGORITHM_SUBSTITUTION_POLICY_LEVELS[algorithm_substitution_policy]
                        <= ALGORITHM_SUBSTITUTION_POLICY_LEVELS[AlgorithmSubstitutionPolicy.NONE]
                    ):
                        msg = "'{}' is not a valid {} value for parameter {}".format(
                            change.new_value, param_props['type'].name, change.kisao_id)
                        raise ValueError(msg)
                    else:
                        msg = "'{}' was ignored because it is not a valid {} value for parameter {}".format(
                            change.new_value, param_props['type'].name, change.kisao_id)
                        warn(msg, BioSimulatorsWarning)

            else:
                if (
                    ALGORITHM_SUBSTITUTION_POLICY_LEVELS[algorithm_substitution_policy]
                    <= ALGORITHM_SUBSTITUTION_POLICY_LEVELS[AlgorithmSubstitutionPolicy.NONE]
                ):
                    msg = "".join([
                        "Algorithm parameter with KiSAO id '{}' is not supported. ".format(change.kisao_id),
                        "Parameter must have one of the following KiSAO ids:\n  - {}".format('\n  - '.join(
                            '{}: {} ({})'.format(kisao_id, param_props['id'], param_props['name'])
                            for kisao_id, param_props in alg_props['parameters'].items())),
                    ])
                    raise NotImplementedError(msg)
                else:
                    msg = "".join([
                        "Algorithm parameter with KiSAO id '{}' was ignored because it is not supported. ".format(change.kisao_id),
                        "Parameter must have one of the following KiSAO ids:\n  - {}".format('\n  - '.join(
                            '{}: {} ({})'.format(kisao_id, param_props['id'], param_props['name'])
                            for kisao_id, param_props in alg_props['parameters'].items())),
                    ])
                    warn(msg, BioSimulatorsWarning)

    # validate variables and setup observables
    invalid_symbols = []
    invalid_targets = []

    all_sbml_ids = rr.model.getAllTimeCourseComponentIds()
    species_sbml_ids = rr.model.getBoundarySpeciesIds() + rr.model.getFloatingSpeciesIds()
    observable_sbml_ids = []

    for variable in variables:
        if variable.symbol:
            if variable.symbol == Symbol.time.value and isinstance(sim, UniformTimeCourseSimulation):
                observable_sbml_ids.append('time')
            else:
                invalid_symbols.append(variable.symbol)

        else:
            sbml_id = target_x_paths_to_sbml_ids.get(variable.target, None)

            if sbml_id and sbml_id in all_sbml_ids:
                if exec_alg_kisao_id != 'KISAO_0000019' and sbml_id in species_sbml_ids:
                    observable_sbml_ids.append('[' + sbml_id + ']')
                else:
                    observable_sbml_ids.append(sbml_id)

            else:
                invalid_targets.append(variable.target)

    if invalid_symbols:
        msg = (
            'The following symbols are not supported:\n  - {}'
            '\n'
            '\n'
            'Only following symbols are supported:\n  - {}'
        ).format(
            '\n  - '.join(sorted(invalid_symbols)),
            '\n  - '.join(sorted([Symbol.time.value])),
        )
        raise NotImplementedError(msg)

    if invalid_targets:
        valid_targets = []
        for species_sbml_id in species_sbml_ids:
            valid_targets.append("/sbml:sbml/sbml:model/sbml:listOfSpecies/sbml:species[@id='{}']".format(species_sbml_id))
        for rxn_id in rr.model.getReactionIds():
            valid_targets.append("/sbml:sbml/sbml:model/sbml:listOfReactions/sbml:reaction[@id='{}']".format(rxn_id))

        msg = (
            'The following targets are not supported:\n  - {}'
            '\n'
            '\n'
            'Only following targets are supported:\n  - {}'
        ).format(
            '\n  - '.join(sorted(invalid_targets)),
            '\n  - '.join(sorted(valid_targets)),
        )
        raise ValueError(msg)

    # simulate
    if isinstance(sim, UniformTimeCourseSimulation):
        number_of_points = (sim.output_end_time - sim.initial_time) / \
            (sim.output_end_time - sim.output_start_time) * sim.number_of_steps + 1
        if abs(number_of_points % 1) > 1e-8:
            msg = (
                'The number of simulation points `{}` must be an integer:'
                '\n  Initial time: {}'
                '\n  Output start time: {}'
                '\n  Output end time: {}'
                '\n  Number of points: {}'
            ).format(number_of_points, sim.initial_time, sim.output_start_time, sim.output_start_time, sim.number_of_points)
            raise NotImplementedError(msg)

        number_of_points = round(number_of_points)
        rr.timeCourseSelections = observable_sbml_ids
        results = numpy.array(rr.simulate(sim.initial_time, sim.output_end_time, number_of_points).tolist()).transpose()
    else:
        rr.steadyStateSelections = observable_sbml_ids
        rr.steadyState()
        results = rr.getSteadyStateValues()

    # check simulation succeeded
    if numpy.any(numpy.isnan(results)):
        msg = 'Simulation failed with algorithm `{}` ({})'.format(exec_alg_kisao_id, alg_props['id'])
        for i_param in range(integrator.getNumParams()):
            param_name = integrator.getParamName(i_param)
            msg += '\n  - {}: {}'.format(param_name, getattr(integrator, param_name))
        raise ValueError(msg)

    # record results
    variable_results = VariableResults()
    for variable, result in zip(variables, results):
        if isinstance(sim, UniformTimeCourseSimulation):
            result = result[-(sim.number_of_points + 1):]

        variable_results[variable.id] = result

    # log action
    log.algorithm = exec_alg_kisao_id
    log.simulator_details = {
        'method': 'simulate' if isinstance(sim, UniformTimeCourseSimulation) else 'steadyState',
        'integrator': integrator.getName(),
    }
    for i_param in range(integrator.getNumParams()):
        param_name = integrator.getParamName(i_param)
        log.simulator_details[param_name] = getattr(integrator, param_name)

    # return results and log
    return variable_results, log


def exec_sed_doc_with_tellurium(doc, working_dir, base_out_path, rel_out_path=None,
                                apply_xml_model_changes=True, return_results=True, report_formats=None, plot_formats=None,
                                log=None, indent=0, pretty_print_modified_xml_models=False,
                                log_level=StandardOutputErrorCapturerLevel.c):
    """
    Args:
        doc (:obj:`SedDocument` or :obj:`str`): SED document or a path to SED-ML file which defines a SED document
        working_dir (:obj:`str`): working directory of the SED document (path relative to which models are located)
        base_out_path (:obj:`str`): path to store the outputs

            * CSV: directory in which to save outputs to files
              ``{base_out_path}/{rel_out_path}/{report.id}.csv``
            * HDF5: directory in which to save a single HDF5 file (``{base_out_path}/reports.h5``),
              with reports at keys ``{rel_out_path}/{report.id}`` within the HDF5 file

        rel_out_path (:obj:`str`, optional): path relative to :obj:`base_out_path` to store the outputs
        apply_xml_model_changes (:obj:`bool`, optional): if :obj:`True`, apply any model changes specified in the SED-ML file before
            calling :obj:`task_executer`.
        return_results (:obj:`bool`, optional): whether to return the result of each output of each SED-ML file
        report_formats (:obj:`list` of :obj:`ReportFormat`, optional): report format (e.g., csv or h5)
        plot_formats (:obj:`list` of :obj:`VizFormat`, optional): plot format (e.g., pdf)
        log (:obj:`SedDocumentLog`, optional): execution status of document
        indent (:obj:`int`, optional): degree to indent status messages
        pretty_print_modified_xml_models (:obj:`bool`, optional): if :obj:`True`, pretty print modified XML models
        log_level (:obj:`StandardOutputErrorCapturerLevel`, optional): level at which to log output

    Returns:
        :obj:`tuple`:

            * :obj:`ReportResults`: results of each report
            * :obj:`SedDocumentLog`: log of the document
    """
    if isinstance(doc, str):
        doc = SedmlSimulationReader().run(doc)

    if not log:
        log = init_sed_document_log(doc)
    start_time = datetime.datetime.now()

    # Set the engine that tellurium uses for plotting
    tellurium.setDefaultPlottingEngine(Config().plotting_engine.value)

    # Create a temporary for tellurium's outputs
    # - Reports: CSV (Rows: time, Columns: data sets)
    # - Plots: PDF
    tmp_out_dir = tempfile.mkdtemp()

    # add a report for each plot to make tellurium output the data for each plot
    for output in doc.outputs:
        if isinstance(output, (Plot2D, Plot3D)):
            report = Report(
                id='__plot__' + output.id,
                name=output.name)

            data_generators = {}
            if isinstance(output, Plot2D):
                for curve in output.curves:
                    data_generators[curve.x_data_generator.id] = curve.x_data_generator
                    data_generators[curve.y_data_generator.id] = curve.y_data_generator

            elif isinstance(output, Plot3D):
                for surface in output.surfaces:
                    data_generators[surface.x_data_generator.id] = surface.x_data_generator
                    data_generators[surface.y_data_generator.id] = surface.y_data_generator
                    data_generators[surface.z_data_generator.id] = surface.z_data_generator

            for data_generator in data_generators.values():
                report.data_sets.append(DataSet(
                    id='__data_set__{}_{}'.format(output.id, data_generator.id),
                    name=data_generator.name,
                    label=data_generator.id,
                    data_generator=data_generator,
                ))

            report.data_sets.sort(key=lambda data_set: data_set.id)
            doc.outputs.append(report)

    filename_with_reports_for_plots = os.path.join(tmp_out_dir, 'simulation.sedml')
    SedmlSimulationWriter().run(doc, filename_with_reports_for_plots, validate_models_with_languages=False)

    # Use tellurium to execute the SED document and generate the specified outputs
    with StandardOutputErrorCapturer(relay=False, level=log_level) as captured:
        try:
            factory = SEDMLCodeFactory(filename_with_reports_for_plots,
                                       workingDir=working_dir,
                                       createOutputs=True,
                                       saveOutputs=True,
                                       outputDir=tmp_out_dir,
                                       )
            for plot_format in (plot_formats or [VizFormat.pdf]):
                factory.reportFormat = 'csv'
                factory.plotFormat = plot_format.value
                factory.executePython()

            log.output = captured.get_text()
            log.export()

        except Exception as exception:
            log.status = Status.FAILED
            log.exception = exception
            log.duration = (datetime.datetime.now() - start_time).total_seconds()
            log.output = captured.get_text()
            for output in log.outputs.values():
                output.status = Status.SKIPPED
            log.export()
            shutil.rmtree(tmp_out_dir)
            raise

    # Convert tellurium's CSV reports to the desired BioSimulators format(s)
    # - Transpose rows/columns
    # - Encode into BioSimulators format(s)
    if return_results:
        report_results = ReportResults()
    else:
        report_results = None

    for report_filename in glob.glob(os.path.join(tmp_out_dir, '*.csv')):
        report_id = os.path.splitext(os.path.basename(report_filename))[0]
        is_plot = report_id.startswith('__plot__')
        if is_plot:
            output_id = report_id[len('__plot__'):]
        else:
            output_id = report_id

        log.outputs[output_id].status = Status.RUNNING
        log.export()
        output_start_time = datetime.datetime.now()

        # read report from CSV file produced by tellurium
        data_set_df = pandas.read_csv(report_filename).transpose()

        # create pseudo-report for ReportWriter
        output = next(output for output in doc.outputs if output.id == report_id)
        if is_plot:
            output.id = output_id
        data_set_results = DataSetResults()
        for data_set in output.data_sets:
            if is_plot:
                data_set.id = data_set.id[len('__data_set__{}_'.format(output_id)):]
            data_set_results[data_set.id] = data_set_df.loc[data_set.label, :].to_numpy()

        # append to data structure of report results
        if return_results:
            report_results[output_id] = data_set_results

        # save file in desired BioSimulators format(s)
        for report_format in report_formats:
            ReportWriter().run(output,
                               data_set_results,
                               base_out_path,
                               os.path.join(rel_out_path, output_id) if rel_out_path else output_id,
                               format=report_format)

        log.outputs[output_id].status = Status.SUCCEEDED
        log.outputs[output_id].duration = (datetime.datetime.now() - output_start_time).total_seconds()
        log.export()

    # Move the plot outputs to the permanent output directory
    out_dir = base_out_path
    if rel_out_path:
        out_dir = os.path.join(out_dir, rel_out_path)

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    for plot_format in plot_formats:
        for plot_filename in glob.glob(os.path.join(tmp_out_dir, '*.' + plot_format.value)):
            shutil.move(plot_filename, out_dir)

    # finalize log
    log.status = Status.SUCCEEDED
    log.duration = (datetime.datetime.now() - start_time).total_seconds()
    log.export()

    # Clean up the temporary directory for tellurium's outputs
    shutil.rmtree(tmp_out_dir)

    # Return a data structure with the results of the reports
    return report_results, log
