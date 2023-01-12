import openai
import os

openai.api_key = os.getenv("OPEN_API_KEY")

def separateBy(text, sep):
    ret = []
    for line in text.split("\n"):
        if len(line) <= 1:
            continue
        splitUp = line.split(sep)
        if len(splitUp) != 2:
            continue
        before, after = splitUp[0], splitUp[1]
        before.strip()
        after.strip()
        if before != after:
            ret.append((before, after))
    return ret

def fixGrammar(paragraph):

    prompt = "Consider this paragraph: " + paragraph + "\nList all grammar mistakes on separate lines. For each grammar mistake, write the mistake and correction with a dollar sign in between. If there are no grammar mistakes, output None."
    response = openai.Completion.create(
        model="text-davinci-001",
        prompt=prompt,
        max_tokens=1000,
        temperature=0
    )
    if response.choices[0].text.strip() == "None":
        return []
    
    return separateBy(response.choices[0].text, "$")

def fixStyle(paragraph):
    #make sure there are no illogical sentences

    prompt = "Consider this paragraph: " + paragraph + "\nList any sentences that don't make any sense, separating each sentence with a dollar sign. If all sentences make sense, output a dollar sign."
    illogical = openai.Completion.create(
        model="text-davinci-001",
        prompt=prompt,
        max_tokens=2000,
        temperature=0
    ).choices[0].text.strip().split("$")

    contractions = []
    
    allContractions = []
    f = open("contractionList.txt", "r")
    for line in f:
        a, b = line.split(":")
        a.strip()
        b.strip()
        a.replace("(informal)", "")
        a.replace("(formal)", "")
        allContractions.append((a, b))
    f.close()
    lowered = paragraph.lower()
    for c in allContractions:
        if c[0] in lowered:
            contractions.append(c)
    
    prompt = "Consider this paragraph: " + paragraph + "\nList every sentence written in first person on a separate line. If there are no sentences written in first person, output None."
    response = openai.Completion.create(
        model="text-davinci-001",
        prompt=prompt,
        max_tokens=1000,
        temperature=0
    ).choices[0].text.strip().split("\n")
    firstPerson = response
    if response[0] == "None":
        firstPerson = []

    return [illogical, contractions, firstPerson]

def giveAdvice(intro, body, outro, paragraph):
    type = "introduction"
    if body:
        type = "body"
    elif outro:
        type = "conclusion"
    prompt = "Consider this " + type + " paragraph of an essay: " + paragraph + " What advice is there to improve it?"
    return openai.Completion.create(
        model="text-davinci-001",
        prompt=prompt,
        max_tokens=1000,
        temperature=0.75
    ).choices[0].text.strip()

def main(paragraphs):
    output = []
    for i in range(len(paragraphs)):
        paragraphs[i].replace("$","")
        current = {}
        intro = (i == 0)
        outro = (i + 1 == len(paragraphs))
        body = not intro and not outro

        grammar = fixGrammar(paragraphs[i].strip())
        style = fixStyle(paragraphs[i])
        advice = giveAdvice(intro, body, False, paragraphs[i])
        
        current["grammar"] = grammar
        current["advice"] = advice
        current["illogical"] = style[0]
        current["contractions"] = style[1]
        current["first person"] = style[2]
        output.append(current)
    
    return output