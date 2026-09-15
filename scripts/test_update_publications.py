import copy
import unittest
from unittest.mock import Mock
from update_publications import base_record,merge,parse_dblp,scholar_rows,verify_scholar_record
from translate_locales import validate

class PublicationUpdates(unittest.TestCase):
 def paper(self,title='A Study',source='https://dblp.org/rec/test',doi='10.1/test'):
  return base_record(title,['Yushi Wei','Hai-Ning Liang'],2026,'Test','journal','https://doi.org/'+doi,source,doi)
 def test_duplicate_doi_preserves_curated_content_and_is_idempotent(self):
  old=self.paper();old['topics']=['games'];old['image']={'path':'images/existing.png'}
  new=self.paper(source='https://scholar.google.com/citations?paper=new')
  records=[old];self.assertEqual(merge(records,[new]),[])
  snapshot=copy.deepcopy(records);merge(records,[new]);self.assertEqual(records,snapshot)
  self.assertEqual(old['topics'],['games']);self.assertEqual(old['image']['path'],'images/existing.png')
 def test_addition_does_not_remove_old_papers(self):
  records=[self.paper()];new=self.paper('Another Study','https://dblp.org/rec/new','10.1/new')
  self.assertEqual(merge(records,[new]),[new['id']]);self.assertEqual(len(records),2)
 def test_publisher_version_promotes_preprint_without_changing_id(self):
  old=self.paper();old['kind']='preprint';old['image']={'path':'existing.png'};key=old['id']
  merge([old],[self.paper(source='https://dblp.org/rec/final')])
  self.assertEqual(old['kind'],'journal');self.assertEqual(old['id'],key);self.assertEqual(old['image']['path'],'existing.png')
 def test_blocked_scholar_is_not_empty_success(self):
  with self.assertRaises(ValueError):scholar_rows('<html>Verify you are human</html>')
 def test_scholar_requires_scholarly_type_and_correct_author(self):
  session=Mock();response=session.get.return_value
  item={'title':['A Study'],'type':'journal-article','author':[{'given':'Yushi','family':'Wei'},{'given':'Hai-Ning','family':'Liang'}],'published':{'date-parts':[[2026]]},'DOI':'10.1/test'}
  response.json.return_value={'message':item}
  self.assertIsNotNone(verify_scholar_record(session,self.paper()))
  item['type']='dataset';self.assertIsNone(verify_scholar_record(session,self.paper()))
  item['type']='journal-article';item['author']=[{'given':'Another','family':'Person'}]
  self.assertIsNone(verify_scholar_record(session,self.paper()))
 def test_translation_must_cover_every_string_without_changing_numbers(self):
  with self.assertRaises(ValueError):validate(['March 2025'],{})
  with self.assertRaises(ValueError):validate(['March 2025'],{'March 2025':'mars 2024'})
  self.assertEqual(validate(['March 2025'],{'March 2025':'mars 2025'}),{'March 2025':'mars 2025'})
 def test_dblp_author_order_and_empty_source_protection(self):
  def row(author,position):return {k:{'value':str(v)} for k,v in dict(pub='https://dblp.org/rec/a',title='Test.',year=2026,kind='http://bibtex#Article',author=author,position=position).items()}
  result=parse_dblp({'results':{'bindings':[row('Hai-Ning Liang',2),row('Yushi Wei',1)]}})
  self.assertEqual(result[0]['authors'],['Yushi Wei','Hai-Ning Liang'])
  with self.assertRaises(ValueError):parse_dblp({'results':{'bindings':[]}})
  with self.assertRaises(ValueError):parse_dblp({'results':{'bindings':[row('Hai-Ning Liang',2)]}})
if __name__=='__main__':unittest.main()
