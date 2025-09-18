import os
import getout_of_text_3 as got3

TEST_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_sample():
    return got3.read_corpora(TEST_DIR, 'sample', genre_list=['blog','news'])

def test_read_corpora():
    data = load_sample()
    assert 'blog' in data and 'news' in data
    assert len(data['blog']) > 0

def test_search_keyword():
    data = load_sample()
    res = got3.search_keyword_corpus('justice', data, output='json')
    total_hits = sum(len(v) for v in res.values())
    assert total_hits >= 2

def test_frequency_analysis():
    data = load_sample()
    freq = got3.keyword_frequency_analysis('justice', data, relative=False)
    assert freq['total_count'] >= 2
    assert any(r['genre']=='blog' for r in freq['by_genre'])

def test_collocates():
    data = load_sample()
    coll = got3.find_collocates('justice', data, window_size=3, min_freq=1)
    assert 'all_collocates' in coll
