import inspect

from async_logging import LogLevelName, Logger, LoggingConfig
from cocoa.cli import CLI, ImportType

from cfn_check.cli.utils.attributes import bind
from cfn_check.cli.utils.files import load_templates
from cfn_check.evaluation.validate import ValidationSet
from cfn_check.logging.models import InfoLog
from cfn_check.collection.collection import Collection
from cfn_check.validation.validator import Validator


@CLI.command()
async def validate(
    path: str,
    file_pattern: str | None = None,
    rules: ImportType[Collection] = None,
    tags: list[str] = [
        'Ref',
        'Sub',
        'Join',
        'Select',
        'Split',
        'GetAtt',
        'GetAZs',
        'ImportValue',
        'Equals',
        'If',
        'Not',
        'And',
        'Or',
        'Condition',
        'FindInMap',
    ],
    log_level: LogLevelName = 'info',
):
    '''
    Validate Cloud Foundation
    
    @param rules Path to a file containing Collections
    @param file_pattern A string pattern used to find template files
    @param tags List of CloudFormation intrinsic function tags
    @param log_level The log level to use
    '''

    logging_config = LoggingConfig()
    logging_config.update(
        log_level=log_level,
        log_output='stderr',
    )

    logger = Logger()

    templates = await load_templates(
        path,
        tags,
        file_pattern=file_pattern,
    )

    validation_set = ValidationSet([ 
        bind(
            rule,
            validation,
        )
        for rule in rules.data.values()
        for _, validation in inspect.getmembers(rule)
        if isinstance(validation, Validator)
    ])
    
    if validation_error := validation_set.validate(templates):
        raise validation_error
    
    templates_evaluated = len(templates)
    
    await logger.log(InfoLog(message=f'✅ {validation_set.count} validations met for {templates_evaluated} templates'))
    