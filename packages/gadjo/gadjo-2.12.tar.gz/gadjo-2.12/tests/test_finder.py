import gadjo.finders


def test_finder():
    finder = gadjo.finders.XStaticFinder()
    assert len(finder.find(path='', all=True)) == 4
