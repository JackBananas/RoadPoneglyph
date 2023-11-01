# Main script to track the Chapter release

# Module importation
import yaml
import time

# la creme de la creme
from logbook import update_logbook

# Logging
import logging

logging.basicConfig(level=logging.DEBUG)
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
    # Read configuration file
    log.debug(f'Reading configuration file: {punk_records}')
    with open(punk_records, 'r') as file:
        conf = yaml.safe_load(file)
    # Read logbook file
    logbook_file = conf['logbook']['logbook']
    log.debug(f'Reading logbook file: {logbook_file}')
    with open(logbook_file, 'r') as file:
        logbook = yaml.safe_load(file)

    # Last chapter in the logbook
    last_chapter = logbook[0]['Chapter']
    log.info(f'Last chapter logged: {last_chapter["manga"]} {last_chapter["number"]}')
    
    # Flow control variable init
    log.info('Starting our adventure!')
    count = 0
    cooldown = conf['flow']['cooldown']
    max_count = conf['flow']['max_count']
    live_chapter = last_chapter
    # Flow control loop
    while live_chapter['number'] == last_chapter['number'] and count < max_count:
        # Sequence count
        count += 1
        log.info(f'Sequence counter = {count} / {max_count}')
        
        # Update logbook with the online list of chapters
        logbook = update_logbook(
            url=conf['online']['base_url']+conf['online']['manga_url']
        )
        live_chapter = logbook[0]['Chapter']
        log.info(f'Last chapter logged: {last_chapter["manga"]} {last_chapter["number"]}')
        log.info(f'Last chapter online: {live_chapter["manga"]} {live_chapter["number"]}')

        # Conditional flow
        if last_chapter['number'] == live_chapter['number']:
            log.info(f'No release yet. Keep trying fellow {last_chapter["manga"]} addict')

        elif last_chapter['number'] < live_chapter['number']:
            log.critical(f'This is a new {last_chapter["manga"]} chapter!!!')
            log.info(f'{last_chapter["manga"]} Chapter {last_chapter["number"]}: {last_chapter["title"]}')
            log.info('Writing logbook with the new online information')
            with open(logbook_file, 'w') as file:
                yaml.dump(logbook, file)
            # tell_morgans()
            break

        else:
            log.critical(
                "Local chapter is bigger than online info. Don't ask me what, but something is wrong. "
                "Please, review the local logbook and the online source"
            )
                
        # Cooldown time
        log.info(f'Cooling down for {cooldown}s = {int(cooldown/60):02d}m {cooldown%60:02d}s')
        time.sleep(cooldown)

# =============================================================================


if __name__ == '__main__':
    log.info('*** PROGRAM START ***')
    
    romance_dawn(
        punk_records='punk_records.yml'
    )

    log.info('*** END OF PROGRAM ***')

# =============================================================================
