from lxml import etree as ET
import json
import requests
import re

# Udify Prediction Handler
def udify_predict(text):
    tokens = text.strip()
    tokens = re.sub("([a-zA-Z]+)(n['’]t)", "\\1 \\2", tokens) # split "don't" to "do" "n't"
    tokens = re.sub("I['’]m", "I am", tokens)
    tokens = re.sub("([a-zA-Z]+)['’]re", "\\1 are", tokens)
    tokens = re.sub("([a-zA-Z]+)['’]d", "\\1 would", tokens)
    tokens = re.sub("([a-zA-Z]+)['’]ve", "\\1 have", tokens)
    
    response = requests.post("http://ud-parser:8888/predict", json.dumps({"text": tokens}))
    if response.status_code == 200:
        return json.loads(response.text)["result"]
    else:
        raise ValueError("Udify predict Error")

        
# Convert Token String to Tree
def ud2subtree(ud, primary_idx):
    subtree = ET.Element("dt")
    primary_word = None
    for idx, head in enumerate(ud["predicted_heads"]):
        if head - 1 == primary_idx:
            subtree.append(ud2subtree(ud, idx))
        elif idx == primary_idx:
            primary_word = ET.Element("pw")
            subtree.append(primary_word)
            subtree.set("word", ud["words"][idx])
            subtree.set("lemma", ud["lemmas"][idx])
            subtree.set("dependency", ud["predicted_dependencies"][idx])
            subtree.set("upos", ud["upos"][idx])
            subtree.set("sep", ud["seps"][idx])
            subtree.set("feats", ud["feats"][idx] if ud["feats"][idx] != "_" else "")
            subtree.set("idx", str(idx))
    if len(subtree) == 1:
        subtree.remove(primary_word)
    return subtree

def ud2tree(ud, sentence):
    seps = []
    s = " "+sentence
    for word in ud["words"]:
        idx = s.find(word)
        seps.append(s[0:idx])
        s = s[idx+len(word):]
    ud["seps"] = seps

    if ud["words"][-1] == ".":
        ud["words"] = ud["words"][:-1]
        ud["lemmas"] = ud["lemmas"][:-1]
        ud["predicted_heads"] = ud["predicted_heads"][:-1]
        ud["predicted_dependencies"] = ud["predicted_dependencies"][:-1]
        ud["upos"] = ud["upos"][:-1]
        ud["seps"] = ud["seps"][:-1]
        ud["feats"] = ud["feats"][:-1]
    
    if ud["lemmas"][0][0] == ud["lemmas"][0][0].lower():
        ud["words"][0] = ud["words"][0][0].lower() + ud["words"][0][1:]
    
    tree = None
    for idx, head in enumerate(ud["predicted_heads"]):
        if head == 0:
            tree = ud2subtree(ud, idx)
            break
    return tree

def sentence2tree(sentence):
    ud = udify_predict(sentence)
    return ud2tree(ud, sentence)

# Convert Tree to Token List
def tree2tokenlist(tree, token="word"):
    enumerated_token_list = subtree2enumerated_tokenlist(tree, token)
    enumerated_token_list.sort(key=lambda x: x[1])
    return [enumerated_token[0] for enumerated_token in enumerated_token_list]
    
def subtree2enumerated_tokenlist(tree, token):
    if type(tree) == str:
        tree = ET.fromstring(tree)
    if len(tree) == 0:
        return [(tree.attrib[token], int(tree.attrib["idx"]))]
    else:
        retval = []
        for child in tree:
            if child.tag == "pw":
                retval.append((tree.attrib[token], int(tree.attrib["idx"])))
            elif child.tag == "dt":
                retval.extend(subtree2enumerated_tokenlist(child, token))
        return retval

# Convert Token List to Index List
def tokenlist2indexlist(tokenlist, word2index):
    return [word2index[token] if token in word2index else word2index["_OOV_"] for token in tokenlist]


# View Entry as Text
def view_entry(entry):
    return "[{}: {}]".format("T" if entry["sign"] else "F", " ".join(tree2tokenlist(entry["tree"])))

# View Tableau as Text
def view_tableau(tableau):
    if type(tableau) is str:
        tableau = json.loads(tableau)
    if "root" in tableau:
        tableau = tableau["root"]
    retval = ""
    retval += " ".join([view_entry(entry) for entry in tableau["entries"]]) + "\n"
    for i, child_node in enumerate(tableau["child_nodes"]):
        lines = view_tableau(child_node).split("\n")
        for j, line in enumerate(lines):
            if i == len(tableau["child_nodes"]) - 1:
                retval += ("└" if j == 0 else "  ") + line + "\n"
            else:
                retval += ("├" if j == 0 else "│") + line + "\n"
    return retval.rstrip()