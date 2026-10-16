import copy
import unittest
from unittest.mock import Mock
from update_publications import base_record,merge,parse_dblp,scholar_rows,verify_scholar_record,topic_tags
from translate_locales import validate

class PublicationUpdates(unittest.TestCase):
 def paper(self,title='A Study',source='https://dblp.org/rec/test',doi='10.1/test'):
  return base_record(title,['Yushi Wei','Hai-Ning Liang'],2026,'Test','journal','https://doi.org/'+doi,source,doi)
 def test_duplicate_doi_preserves_curated_content_and_is_idempotent(self):
  old=self.paper();old['topics']=['gaming'];old['image']={'path':'images/existing.png'}
  new=self.paper(source='https://scholar.google.com/citations?paper=new')
  records=[old];self.assertEqual(merge(records,[new]),[])
  snapshot=copy.deepcopy(records);merge(records,[new]);self.assertEqual(records,snapshot)
  self.assertEqual(old['topics'],['gaming']);self.assertEqual(old['image']['path'],'images/existing.png')
 def test_new_papers_can_span_the_requested_research_areas(self):
  self.assertEqual(topic_tags('Acceptance of Virtual Reality Exergames Among Chinese Older Adults'),['gaming','interaction-tech','accessibility'])
  self.assertEqual(topic_tags('Say it or AI it: Evaluating Hands-Free Text Correction in Virtual Reality'),['interaction-tech','text-entry','ai'])
 def test_gaze_input_is_interaction_without_implying_ai_or_disability(self):
  self.assertEqual(topic_tags('Exploring and Modeling Gaze-Based Steering Behavior in Virtual Reality'),['interaction-tech'])
  self.assertEqual(topic_tags('Infrared motion detection and electromyographic gesture recognition for navigating 3D environments'),['interaction-tech'])
 def test_learning_and_visual_text_do_not_imply_ai_or_text_entry(self):
  self.assertEqual(topic_tags('Cross-cultural factors influencing the adoption of virtual reality for practical learning'),['interaction-tech'])
  self.assertEqual(topic_tags('Visual harmony: text-visual interplay in circular infographics'),['interaction-tech'])
 def test_ai_and_text_entry_have_specific_signals(self):
  self.assertEqual(topic_tags('A Unified Gradient Regularization Family for Adversarial Examples'),['ai'])
  self.assertEqual(topic_tags('Contextual Recovery: Guiding Hand Tracking Failures Recovery in Mixed Reality via VLM Reasoning'),['interaction-tech','ai'])
  self.assertEqual(topic_tags('OnArmQWERTY: An Empirical Evaluation of On-Arm Tap Typing for AR HMDs'),['interaction-tech','text-entry'])
 def test_unrelated_historical_papers_remain_in_all(self):
  self.assertEqual(topic_tags('Crystal structures and magnetic performance of nanocrystalline Sm-Co compounds'),[])
 def test_addition_does_not_remove_old_papers(self):
  records=[self.paper()];new=self.paper('Another Study','https://dblp.org/rec/new','10.1/new')
  self.assertEqual(merge(records,[new]),[new['id']]);self.assertEqual(len(records),2)
 def test_publisher_version_promotes_preprint_without_changing_id(self):
  old=self.paper();old['kind']='preprint';old['image']={'path':'existing.png'};key=old['id']
  old.update(published_date='2025-11-01',published_date_source='https://arxiv.org/abs/example',published_date_basis='first-submission')
  merge([old],[self.paper(source='https://dblp.org/rec/final')])
  self.assertEqual(old['kind'],'journal');self.assertEqual(old['id'],key);self.assertEqual(old['image']['path'],'existing.png')
  self.assertNotIn('published_date',old)
 def test_date_sources_are_preserved_on_repeated_imports(self):
  old=self.paper();old.update(published_date='2026-03',published_date_source='https://api.crossref.org/example',published_date_basis='published-online')
  new=self.paper();new.update(published_date='2026-04-01',published_date_source='https://api.crossref.org/later',published_date_basis='published-print')
  merge([old],[new]);self.assertEqual(old['published_date'],'2026-03');self.assertEqual(old['published_date_basis'],'published-online')
 def test_publisher_promotion_uses_new_version_date(self):
  old=self.paper();old['kind']='preprint';old.update(published_date='2025-11-01',published_date_source='https://arxiv.org/abs/example')
  new=self.paper();new.update(published_date='2026-02',published_date_source='https://api.crossref.org/example',published_date_basis='published-online')
  merge([old],[new]);self.assertEqual(old['published_date'],'2026-02');self.assertEqual(old['published_date_basis'],'published-online')
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
