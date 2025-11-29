from num2words import num2words

def price_in_words(value):
    try:
        value = float(value)
        rupees = int(value)
        paise = int(round((value - rupees) * 100))

        words = num2words(rupees, lang='en_IN').title() + " Rupees"
        if paise:
            words += " and " + num2words(paise, lang='en_IN').title() + " Paise"
        return words + " Only"
    except Exception as e:
        return f"Invalid amount: {e}"
