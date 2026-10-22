"""A media reimport must not republish an author-withheld manuscript."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import import_publication_media as importer

class WithheldImport(unittest.TestCase):
    def test_reimport_keeps_withheld_paper_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();library=root/'private';library.mkdir()
            paper={'id':'withheld','title':'Window placement','doi':'10.1/withheld',
                   'sources':['https://dblp.org/rec/test'],'full_text_access':'withheld',
                   'download_label':'Shi-ISS26-WindowPlacement'}
            (root/'data/publications.json').write_text(json.dumps({'publications':[paper]}))
            (root/'data/publication-pdf-review.json').write_text('[]')
            (library/'manifest.json').write_text(json.dumps({'items':[{'key':'test',
                'file':'private-paper.pdf','title':paper['title'],'doi':paper['doi'],
                'sha256':'0'*64,'version':'acceptedVersion'}]}))
            with patch.object(importer,'ROOT',root), patch('sys.argv',['import','--library',str(library),'--apply']), contextlib.redirect_stdout(io.StringIO()):
                importer.main()
            saved=json.loads((root/'data/publications.json').read_text())['publications'][0]
            self.assertEqual(saved,paper)
            self.assertFalse((root/'downloads').exists())
            report=json.loads((root/'data/publication-media-import.json').read_text())
            self.assertEqual(report['withheld'],['withheld'])
            self.assertEqual(report['added_pdfs'],[])

if __name__=='__main__':unittest.main()
