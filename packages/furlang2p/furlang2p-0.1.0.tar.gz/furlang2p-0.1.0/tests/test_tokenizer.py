from furlan_g2p.config.schemas import TokenizerConfig
from furlan_g2p.tokenization.tokenizer import Tokenizer


def test_abbreviation_blocks_sentence_split() -> None:
    cfg = TokenizerConfig(abbrev_no_split={"sig"})
    tok = Tokenizer(cfg)
    text = "Al è rivât il Sig. Bepo. O ven?"
    assert tok.split_sentences(text) == [
        "Al è rivât il Sig. Bepo.",
        "O ven?",
    ]


def test_split_words_apostrophes_and_pauses() -> None:
    tok = Tokenizer()
    sent = "L’aghe, cjase! _ __"
    assert tok.split_words(sent) == ["l'aghe", "cjase", "_", "__"]
