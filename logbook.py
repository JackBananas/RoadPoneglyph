# Script with the Chapter class to support the journey
import os

# Module importation
import yaml
import requests
from bs4 import BeautifulSoup
import time
from git import Repo

# Logging
import logging
log = logging.getLogger(__name__)

# =============================================================================


def fetch_url(
        url: str
) -> dict[str:str]:
    """
    Returns the last chapter from the online source
    INPUTS
        url :: url with the list of chapters online
    OUTPUT
        dict with info about the last chapter online
    """
    log.info(f'Fetching {url} to retrieve the List of Chapters')
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    # Look in all the links
    log.warning('Search criteria may be modified for other manga or site')
    for a in soup.find_all('a', href=True):
        # Only in the links with text and format
        if a.find('div'):
            # Only in links with info in text
            if ' Chapter ' in a.find('div').text:
                # log.debug(f'Found {a.find("div").text}')
                return dict(
                    url=a['href'],
                    manga=a.find_all('div')[0].text.split(' Chapter ')[0],
                    number=a.find_all('div')[0].text.split(' Chapter ')[1],
                    title=a.find_all('div')[1].text
                )

# =============================================================================


class Logbook:
    def __init__(
            self,
            logbook_file: str
    ) -> None:
        """
        Reads the file and Init the class with the attrs:
            file :: logbook abs filepath
            chapters :: logbook in the form of a list of chapters with info
            release :: bool to track a new release
        """
        # Abs path for the logbook file
        pathfile = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                logbook_file
            )
        )
        # Init attr
        self.file: str = pathfile
        log.info(f'Reading logbook logbook_file: {logbook_file}')
        with open(pathfile, 'r') as f:
            self.chapters: list[dict[str:dict[str:str]]] = yaml.safe_load(f)
        log.debug(f'Found {len(self.chapters)} chapters logged')
        log.info(f'Last chapter logged: {self.chapters[0]["Chapter"]["manga"]} {self.chapters[0]["Chapter"]["number"]} - {self.chapters[0]["Chapter"]["title"]}')

    def update(
            self,
            url: str,
            cooldown: int,
            max_count: int,
    ) -> None:
        """
        Fetches the online source recursively until a new chapter is found.
        Then, triggers the release sequence.
        INPUTS
            url :: url with the list of chapters online
            cooldown :: time between loops
            max_count :: flow loop exit condition
        OUTPUT
            None
        """
        # Init flow variables
        count = 0
        last = self.chapters[0]['Chapter']
        # Flow control loop
        while count < max_count:
            # Sequence count
            count += 1
            log.info(f'Sequence counter = {count} / {max_count}')

            # Update logbook with the online list of chapters
            live = fetch_url(url=url)
            log.info(f'Last chapter logged: {last["manga"]} {last["number"]}')
            log.info(f'Last chapter online: {live["manga"]} {live["number"]}')

            # Conditional flow
            if last['number'] == live['number']:
                log.info(f'No release yet. Keep trying fellow {live["manga"]} addict')

            elif last['number'] < live['number']:
                log.critical(f'This is a new {live["manga"]} chapter!!!')
                log.info(f'{live["manga"]} Chapter {live["number"]} - {live["title"]}')
                self._release_sequence(
                    new_chapter=live
                )
                break

            else:
                log.exception(
                    "Local chapter is bigger than online info. Don't ask me what, but something is wrong. "
                    "Please, review the local logbook and the online source"
                )

            # Cooldown time
            log.info(f'Cooling down for {cooldown}s = {int(cooldown / 60):02d}m {cooldown % 60:02d}s')
            time.sleep(cooldown)

    def _release_sequence(
            self,
            new_chapter: dict[str, str]
    ):
        log.debug('Init release sequence')
        self.chapters.insert(0, dict(Chapter=new_chapter))
        self._write()
        self._git_push()
        log.warning('TBI notification to the users')

    def _write(self) -> None:
        log.info('Writing logbook with the new online information')
        with open(self.file, 'w') as f:
            yaml.dump(self.chapters, f)

    def _git_push(self) -> None:
        # Git path
        git_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                '.git/'
            )
        )
        log.debug('Init git repository')
        repo = Repo(git_path)

        log.debug('Add the logbook to Git')
        repo.index.add(os.path.basename(self.file))

        msg = f'Added {self.chapters[0]["Chapter"]["manga"]} Chapter {self.chapters[0]["Chapter"]["number"]}'
        log.info(f'Commit logbook to git with message = {msg}')
        repo.index.commit(msg)

        branch = 'main'
        log.info(f'Push changes to the remote {branch} branch')
        repo.git.push('origin', branch)
        log.warning('Need to change the remote branch')

        # Close the git repository
        repo.close()

# =============================================================================
