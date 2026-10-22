import copy
import unittest
from publication_labels import assign_labels, candidate
from update_publications import merge

def paper(id='a', **kwargs):
    return dict(id=id, title='Window placement in virtual reality', authors=['Rongkai Shi'],
                venue='CHI', year=2026, kind='conference', pdf='shared.pdf',
                doi='', sources=['https://example.org/'+id], urls=[], **kwargs)

class DownloadLabels(unittest.TestCase):
    def test_requested_names(self):
        self.assertEqual(candidate(paper('xr-window-placement-2026')), 'Shi-ISS26-WindowPlacement')
        p=paper('scalecue-wim-2026');p['authors']=['Junkun Long']
        self.assertEqual(candidate(p),'Long-VRST26-ScaleCueWIM')
    def test_stable_after_metadata_and_repeat_assignment(self):
        p=paper();assign_labels([p]);label=p['download_label']
        p.update(title='New title', year=2027, venue='TVCG');assign_labels([p])
        self.assertEqual(p['download_label'],label)
        new=copy.deepcopy(p);new['sources']=['https://example.org/publisher']
        merge([p],[new]);self.assertEqual(p['download_label'],label)
    def test_collisions_are_case_insensitive_and_existing_names_win(self):
        a,b=paper('a'),paper('b');assign_labels([a]);saved=a['download_label']
        assign_labels([b,a]);self.assertEqual(a['download_label'],saved)
        self.assertNotEqual(a['download_label'].casefold(),b['download_label'].casefold())
        snapshot=copy.deepcopy([a,b]);assign_labels([a,b]);self.assertEqual([a,b],snapshot)
    def test_supplement_is_not_full_paper(self):
        p=paper(pdf_metadata={'document_kind':'supplement'})
        self.assertTrue(candidate(p).endswith('-Supplement'))
    def test_external_and_local_records_share_convention_without_changing_urls(self):
        a,b=paper('a'),paper('b');del b['pdf'];b['pdf_url']='https://example.org/publisher.pdf'
        before=copy.deepcopy([a,b]);assign_labels([a,b])
        self.assertEqual(a['pdf'],before[0]['pdf']);self.assertEqual(b['pdf_url'],before[1]['pdf_url'])
    def test_unsafe_or_ambiguous_metadata_requires_curation(self):
        p=paper();p['venue']='Unknown Conference'
        with self.assertRaises(ValueError):candidate(p)
        p['download_label']='../../unsafe'
        with self.assertRaises(ValueError):assign_labels([p])
    def test_duplicate_persisted_labels_fail(self):
        a,b=paper('a'),paper('b');assign_labels([a]);b['download_label']=a['download_label']
        with self.assertRaises(ValueError):assign_labels([a,b])

if __name__=='__main__':unittest.main()
