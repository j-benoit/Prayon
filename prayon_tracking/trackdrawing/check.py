from spellchecker import SpellChecker
from .models import ExtractSAP


def check_database():
    spell = SpellChecker(language='fr')
    records =ExtractSAP.objects.filter(status__in=['CLOSED', 'CHECKED', 'INVALID']).order_by('id')[:100]
    spell.word_frequency.add('reparation')
    for record in records:
        mispelled_words = spell.unknown(spell.split_words(record.title))
        if mispelled_words:
            for word in mispelled_words:
                print(record.id, ' : ', word, ' ==> ', spell.correction(word))
        else:
            print(record.id, ' : No error')
