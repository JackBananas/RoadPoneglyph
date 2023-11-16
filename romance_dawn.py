# Main script to track the Chapter release

# Module importation
import os.path
import yaml

# la creme de la creme
from logbook import Logbook

# Logging
import logging
log = logging.getLogger(__name__)

# =============================================================================


def romance_dawn(
    punk_records: str,
) -> None:
    """
    Main function with the whole structure of the activity:
        1. Read configuration file
        2. Read logbook with all the locally logged chapters
        3. Update logbook with the latest information online
        4. Flow control

    INPUTS
        punk_records :: configuration file in yaml format
    OUTPUT
        None
    """
    # Abs path for the configuration file
    conf_file = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                punk_records
            )
    )
    # Read configuration file
    log.debug(f'Reading configuration file: {os.path.basename(conf_file)}')
    with open(conf_file, 'r') as file:
        conf = yaml.safe_load(file)

    # Init logbook
    logbook = Logbook(
        logbook_file=conf['logbook']['logbook']
    )
    log.info('Starting our adventure!')
    logbook.update(
        url=conf['online']['base_url'] + conf['online']['manga_url'],
        cooldown=conf['flow']['cooldown'],
        max_count=conf['flow']['max_count']
    )

# =============================================================================


if __name__ == '__main__':
    # Set up logging
    from OdensJournal import log_setup
    log_setup()

    log.info('*** PROGRAM START ***')
    romance_dawn(
        punk_records='punk_records.yml'
    )
    log.info('*** END OF PROGRAM ***')

# =============================================================================
