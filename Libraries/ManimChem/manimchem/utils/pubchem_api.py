from typing import Optional
from urllib.parse import quote
import json
import sys


_answers: dict = {}  # url -> (status, text): each molecule is asked of PubChem once per session


def fetch(url: str):
    """Downloads `url`: (status code, text). In Manimator (Python in the browser) the browser makes the request,
    from your own computer; elsewhere Python's urllib does. Successful answers are kept for the session."""
    if url in _answers:
        return _answers[url]
    status, text = _download(url)
    if status == 200:
        _answers[url] = (status, text)
    return status, text


def _download(url: str):
    if sys.platform == "emscripten":
        import js  # Pyodide: the page's JavaScript

        request = js.XMLHttpRequest.new()
        request.open("GET", url, False)  # synchronous: the script waits for the answer
        try:
            request.send(None)
        except Exception as error:  # noqa: BLE001 - a network or policy error
            raise ConnectionError(f"Couldn't reach {url}: {error}") from None
        if request.status == 0:
            raise ConnectionError(f"Couldn't reach {url}")
        return int(request.status), str(request.responseText)

    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


class PubchemAPIManager:
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound"

    def __init__(
        self,
        cid: Optional[int] = None,
        name: Optional[str] = None,
        smiles: Optional[str] = None,
        inchi: Optional[str] = None,
        three_d: bool = False,
        format: str = "json",
    ):
        if not any([cid, name, smiles, inchi]):
            raise Exception(
                "You should provide an identifier. Available identifiers are cid, name, smiles and inchi"
            )
        self.cid = cid
        self.name = name
        self.smiles = smiles
        self.inchi = inchi
        self.three_d = three_d
        self.format = format

    def handle_request(self, status: int, text: str, identifier):
        if status == 200:
            try:
                return json.dumps(json.loads(text))

            except json.JSONDecodeError:
                return text

        if status == 404:
            raise Exception(f"Compound {identifier} not found")

        raise Exception(
            f"An error occurred when calling the Pub Chem API. Status code: {status}. Request response: {text[:500]}"
        )

    def request(self, namespace: str, identifier):
        request_url = f"{PubchemAPIManager.BASE_URL}/{namespace}/{quote(str(identifier), safe='')}/{self.format}"
        if self.three_d:
            request_url += "?record_type=3d"

        status, text = fetch(request_url)
        return self.handle_request(status, text, identifier=identifier)

    def from_cid(self):
        return self.request("cid", self.cid)

    def from_name(self):
        return self.request("name", self.name)

    def from_smiles(self):
        return self.request("smiles", self.smiles)

    def from_inchi(self):
        return self.request("inchikey", self.inchi)

    def get_molecule(self):
        if self.cid:
            return self.from_cid()

        elif self.name:
            return self.from_name()

        elif self.smiles:
            return self.from_smiles()

        elif self.inchi:
            return self.from_inchi()

        else:
            raise Exception("No identifier provided")
