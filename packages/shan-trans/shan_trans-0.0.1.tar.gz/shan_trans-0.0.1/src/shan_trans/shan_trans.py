# Import necessary package (Shan tokenizer)
import pyidaungsu as pds

# Map grapheme / phoneme correspondances
shan_initial = {'ၶျ': 'cʰ', 'သျ': 'ʃ', 'ၵ': 'k', 'ၶ': 'kʰ', 'င': 'ŋ', 'ၸ': 'c', 'သ': 's', 'ၺ': 'ɲ', 'တ': 't', 'ထ': 'tʰ', 'ၼ': 'n', 'ပ': 'p', 'ၽ': 'pʰ', 'ၾ': 'f', 'မ': 'm', 'ယ': 'j', 'ရ': 'r', 'လ': 'l', 'ဝ': 'w', 'ႀ': 'θ', 'ႁ': 'h', 'ဢ': 'ʔ', 'ၷ': 'g', 'ၻ': 'd', 'ၿ': 'b', 'ၹ': 'z', 'ျ': 'j', 'ြ': 'r', 'ႂ': 'w'}
shan_punt_num = {'႐' : 'sǒn', '႑' : 'nɯ̄ŋ', '႒' : 'sɔ̌ŋ', '႓' : 'sǎːm', '႔' : 'sì', '႕' : 'hāː', '႖' : 'hók', '႗' : 'cét', '႘' : 'pɛ̀t', '႙' : 'kāw', '0' : 'sǒn', '1' : ' nɯ̄ŋ ', '2' : 'sɔ̌ŋ', '3' : 'sǎːm', '4' : 'sì', '5' : 'hāː', '6' : 'hók', '7' : 'cét', '8' : 'pɛ̀t', '9' : 'kāw', '႞' : ' nɯ̄ŋ ', '႟' : 'ʔɤ́j', '၊' : ',', '။' : '.'}
shan_diphthong = {'ႂ်ႇ': 'àɯ', 'ႂ်ႈ': 'āɯ', 'ႂ်း': 'áɯ', 'ႂ်ႉ': 'âɯ', 'ႂ်ႊ': 'a᷈ɯ', 'ႂ်': 'ǎɯ', 'ွႆႇ': 'ɔ̀j', 'ွႆႈ': 'ɔ̄j', 'ွႆး': 'ɔ́j', 'ွႆႉ': 'ɔ̂j', 'ွႆႊ': 'ɔ᷈j', 'ွႆ': 'ɔ̌j', 'ႆႃႇ': 'àːj', 'ႆႃႈ': 'āːj', 'ႆႃး': 'áːj', 'ႆႃႉ': 'âːj', 'ႆႃႊ': 'a᷈ːj', 'ႆႃ': 'ǎːj', 'ႆၢႇ': 'àːj', 'ႆၢႈ': 'āːj', 'ႆၢး': 'áːj', 'ႆၢႉ': 'âːj', 'ႆၢႊ': 'a᷈ːj', 'ႆၢ': 'ǎːj', 'ႃႆႇ': 'àːj', 'ႃႆႈ': 'āːj', 'ႃႆး': 'áːj', 'ႃႆႉ': 'âːj', 'ႃႆႊ': 'a᷈ːj', 'ႃႆ': 'ǎːj', 'ၢႆႇ': 'àːj', 'ၢႆႈ': 'āːj', 'ၢႆး': 'áːj', 'ၢႆႉ': 'âːj', 'ၢႆႊ': 'a᷈ːj', 'ၢႆ': 'ǎːj', 'ႆႇ': 'àj', 'ႆႈ': 'āj', 'ႆး': 'áj', 'ႆႉ': 'âj', 'ႆႊ': 'a᷈j', 'ႆ': 'ǎj'}
shan_vowel = {'ိုဝ်': 'ɯ', 'ိူဝ်': 'ɤ', 'ို': 'ɯ', 'ိူ': 'ɤ', 'ူဝ်': 'o', 'ေႃ': 'ɔ', 'ွ': 'ɔ', 'ု': 'u', 'ီ': 'i', 'ိ': 'i', 'ေ': 'e', 'ဵ': 'e', 'ႄ': 'ɛ', 'ႅ' : 'ɛ', 'ႃ': 'aa', 'ၢ': 'aa'}
shan_o = {'ူပ်ႇ': 'òp', 'ူတ်ႇ':'òt', 'ူၵ်ႇ':'òk', 'ူမ်ႇ':'òm', 'ူၼ်ႇ':'òn', 'ူင်ႇ':'òŋ', 'ူၺ်ႇ':'òj', 'ူပ်ႈ':'ōp', 'ူတ်ႈ':'ōt', 'ူၵ်ႈ':'ōk', 'ူမ်ႈ':'ōm', 'ူၼ်ႈ':'ōn', 'ူင်ႈ':'ōŋ', 'ူၺ်ႈ':'ōj', 'ူပ်း':'óp', 'ူတ်း':'ót', 'ူၵ်း':'ók', 'ူမ်း':'óm', 'ူၼ်း':'ón', 'ူင်း':'óŋ', 'ူၺ်း':'ój', 'ူပ်ႉ':'ôp', 'ူတ်ႉ':'ôt', 'ူၵ်ႉ':'ôk', 'ူမ်ႉ':'ôm', 'ူၼ်ႉ':'ôn', 'ူင်ႉ':'ôŋ', 'ူၺ်ႉ':'ôj', 'ူပ်ႊ':'o᷈p', 'ူတ်ႊ':'o᷈t', 'ူၵ်ႊ':'o᷈k', 'ူမ်ႊ':'o᷈m', 'ူၼ်ႊ':'o᷈n', 'ူင်ႊ':'o᷈ŋ', 'ူၺ်ႊ':'o᷈j', 'ူပ်':'ǒp', 'ူတ်':'ǒt', 'ူၵ်':'ǒk', 'ူမ်':'ǒm', 'ူၼ်':'ǒn', 'ူင်':'ǒŋ', 'ူၺ်':'ǒj', 'ူႇ':'ù', 'ူႈ':'ū', 'ူး':'ú', 'ူႉ':'û', 'ူႊ':'u᷈', 'ူ':'ǔ'}
shan_final = {'ၵ်ႇ': '̀k', 'တ်ႇ': '̀t', 'ပ်ႇ': '̀p', 'င်ႇ': '̀ŋ', 'ၼ်ႇ': '̀n', 'မ်ႇ': '̀m', 'ဝ်ႇ': '̀w', 'ၺ်ႇ': '̀j', 'ၵ်ႈ': '̄k', 'တ်ႈ': '̄t', 'ပ်ႈ': '̄p', 'င်ႈ': '̄ŋ', 'ၼ်ႈ': '̄n', 'မ်ႈ': '̄m', 'ဝ်ႈ': '̄w', 'ၺ်ႈ': '̄j', 'ၵ်း': '́k', 'တ်း': '́t', 'ပ်း': '́p', 'င်း': '́ŋ', 'ၼ်း': '́n', 'မ်း': '́m', 'ဝ်း': '́w', 'ၺ်း': '́j', 'ၵ်ႉ': '̂k', 'တ်ႉ': '̂t', 'ပ်ႉ': '̂p', 'င်ႉ': '̂ŋ', 'ၼ်ႉ': '̂n', 'မ်ႉ': '̂m', 'ဝ်ႉ': '̂w', 'ၺ်ႉ': '̂j', 'ၵ်ႊ': '᷈k', 'တ်ႊ': '᷈t', 'ပ်ႊ': '᷈p', 'င်ႊ': '᷈ŋ', 'ၼ်ႊ': '᷈n', 'မ်ႊ': '᷈m', 'ဝ်ႊ': '᷈w', 'ၺ်ႊ': '᷈j', 'ၵ်': '̌k', 'တ်': '̌t', 'ပ်': '̌p', 'င်': '̌ŋ', 'ၼ်': '̌n', 'မ်': '̌m', 'ဝ်': '̌w', 'ၺ်': '̌j',  'ႇ': '̀', 'ႈ': '̄', 'း': '́', 'ႉ': '̂', 'ႊ': '᷈'}
shan_final_a = {'ၵ်ႇ': 'àk', 'တ်ႇ': '̀at', 'ပ်ႇ': '̀ap', 'င်ႇ': 'àŋ', 'ၼ်ႇ': '̀an', 'မ်ႇ': 'àm', 'ဝ်ႇ': '̀aw', 'ၺ်ႇ': '̀aj', 'ၵ်ႈ': 'āk', 'တ်ႈ': 'āt', 'ပ်ႈ': 'āp', 'င်ႈ': 'āŋ', 'ၼ်ႈ': 'ān', 'မ်ႈ': 'ām', 'ဝ်ႈ': 'āw', 'ၺ်ႈ': 'āj', 'ၵ်း': 'ák', 'တ်း': 'át', 'ပ်း': 'áp', 'င်း': 'áŋ', 'ၼ်း': 'án', 'မ်း': 'ám', 'ဝ်း': 'áw', 'ၺ်း': '́aj', 'ၵ်ႉ': 'âk', 'တ်ႉ': 'ât', 'ပ်ႉ': 'âp', 'င်ႉ': 'âŋ', 'ၼ်ႉ': 'ân', 'မ်ႉ': 'âm', 'ဝ်ႉ': 'âw', 'ၺ်ႉ': 'âj', 'ၵ်ႊ': 'a᷈k', 'တ်ႊ': 'a᷈t', 'ပ်ႊ': 'a᷈p', 'င်ႊ': 'a᷈ŋ', 'ၼ်ႊ': 'a᷈n', 'မ်ႊ': 'a᷈m', 'ဝ်ႊ': 'a᷈w', 'ၺ်ႊ': 'a᷈j', 'ၵ်': 'ǎk', 'တ်': 'ǎt', 'ပ်': 'ǎp', 'င်': 'ǎŋ', 'ၼ်': 'ǎn', 'မ်': 'ǎm', 'ဝ်': 'ǎw', 'ၺ်': 'ǎj'}
shan_tone_a ={'ႇ': 'à', 'ႈ': 'ā', 'း': 'á', 'ႉ': 'â', 'ႊ': 'a᷈'}
long_a_tone = {'aǎ': 'ǎː', 'aà': 'àː', 'aā': 'āː', 'aá': 'áː', 'aâ': 'âː', 'aa᷈': 'a᷈ː'}
shan_vocalic_sign = ['ီ', 'ိ', 'ေ', 'ဵ', 'ႄ', 'ႅ', 'ု', 'ူ', 'ႂ်', 'ႆ', 'ွ', 'ႃ', 'ၢ']
shan_tone_sign = ['ႇ', 'ႈ', 'း', 'ႉ', 'ႊ']
ipa_tone = ['̌', '̀', '̄', '́', '̂', '᷈']
shan_minor_syll_check = ['ၵ', 'ၶ', 'င', 'ၸ', 'သ', 'ၺ', 'တ', 'ထ', 'ၼ', 'ပ', 'ၽ', 'ၾ', 'မ', 'ယ', 'ရ', 'လ', 'ဝ', 'ႀ', 'ႁ', 'ဢ', 'ၷ', 'ၻ', 'ၿ', 'ၹ']
shan_punt_num_check = ['႐', '႑', '႒', '႓', '႔', '႕', '႖', '႗', '႘', '႙', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '႞', '႟', '၊', '။']


# Function for transcribing numbers and punctuation signs
def transcribe_punct_num(shan_text):
	for key,value in shan_punt_num.items():
		if key in shan_text:
			shan_text = shan_text.replace(key, value)
			return shan_text

# Function for transcribing and prefixing minor syllables to the next token
def transcribe_minor(shan_text):
	for key,value in shan_initial.items():
		if key in shan_text:
			shan_text = shan_text.replace(key, value)
	shan_text = shan_text + 'ə'
	return shan_text

# Function for transcribing major syllables
def transcribe_major(shan_text):
	#Check for written vowel
	if any(vowel in shan_text for vowel in shan_vocalic_sign):
		# Transcribe final diphthong and tone
		for key,value in shan_diphthong.items():
			if key in shan_text:
				shan_text = shan_text.replace(key, value)
		# Transcribe vowel
		for key,value in shan_vowel.items():
			if key in shan_text:
				shan_text = shan_text.replace(key, value)
		# Transcribe ambiguous grapheme /''ူ/
		for key,value in shan_o.items():
			if key in shan_text:
				shan_text = shan_text.replace(key, value)
	# If no written vowel
	else:
		# Check for asat sign (marking coda consonant)
		if '\u103A' in shan_text:
			# Transcribe coda consonant (as well as tone) with inherent vowel /a/
			for key,value in shan_final_a.items():
				if key in shan_text:
					shan_text = shan_text.replace(key, value)
		# If no coda consonant, transcribe tone sign with inherent vowel /a/
		elif any(tone in shan_text for tone in shan_tone_sign):
			for key,value in shan_tone_a.items():
				if key in shan_text:
					shan_text = shan_text.replace(key, value)
		# If no tone sign, transcribe with inherent vowel and tone /ǎ/
		else:
			shan_text = shan_text + 'ǎ'
	# Transcribe final consonant and tone (if marked vowel)
	for key,value in shan_final.items():
		if key in shan_text:
			shan_text = shan_text.replace(key, value)
	# Transcribe initial consonant(s)
	for key,value in shan_initial.items():
		if key in shan_text:
			shan_text = shan_text.replace(key, value)
	# In open syllable without a tone marker, transcribe inherent rising tone
	if not any(tone in shan_text for tone in ipa_tone):
		shan_text = shan_text + '̌'
	# Make transciption of long /a/ with tone better (aā -> āː)
	for key,value in long_a_tone.items():
		if key in shan_text:
			shan_text = shan_text.replace(key, value)
	return shan_text

def transcibe_shn(shan_text):
    # Tokenize sentence
    tokenized = pds.tokenize(shan_text, lang="shan")

    # Transcribe each token
    transcribed_tokens = []
    for token in tokenized:
        # Check and transcribe punctuation signs and numbers
        if token in shan_punt_num_check:
            transcribed_tokens.append(transcribe_punct_num(token))
        # Check and transcribe minor syllables
        elif token in shan_minor_syll_check:
            transcribed_tokens.append(transcribe_minor(token))
        # Transcribe major syllables
        else:
            transcribed_tokens.append(transcribe_major(token))

    # Join the transcribed token back together in a string
    final_transcription = ' '.join(transcribed_tokens)

    # Attach minor syllables to next major syllable and other cosmetic issues
    final_transcription = final_transcription.replace('ə ', 'ə')
    final_transcription = final_transcription.replace('  ', ' ')
    final_transcription = final_transcription.replace(' .', '.')
    final_transcription = final_transcription.replace(' ,', ',')

    return final_transcription



