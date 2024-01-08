import pandas as pd
import sys
import pickle
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from person import Person
from family_tree import FamilyTree


def get_parser():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input file name")
    parser.add_argument("--center", type=str)
    args = parser.parse_args()
    return args

def check_csv(df):
    id_list = list(df["ID"])
    err_idx = (df["Partner"].dropna().isin(df["ID"]) == False).values
    if sum(err_idx) > 0:
        print("[Error] Check Partner: ", err_idx)
        sys.exit()
    
    child_list = set()
    for children in df["Children"].dropna():
        child = children.split("/")
        for ch in child:
            if not ch in id_list:
                print("[Error] {} does not found".format(ch))
                sys.exit()
        child_list = child_list.union(child)
    child_list = list(child_list)

def get_personal_data(df):
    family = {}
    for i, data in df.iterrows():
        male = data["Sex"] == "Male"
        person = Person(data["ID"], male=male)
        family[data["ID"]] = person
    for i, data in df.iterrows():
        person = family[data["ID"]]
        if str(data["Partner"]) != "nan":
            person.add_partner(family[data["Partner"]])
        
        if str(data["Children"]) != "nan":
            children = data["Children"].split("/")
            children = [family[ch] for ch in children]
            person.add_children(children)
        
        Path("texture").mkdir(exist_ok=True)
        img = make_node_texture(data["Given"], data["Sex"])
        img.save("texture/{}.png".format(data["ID"]))
    return family

def build_family_tree(family, center=None):
    if center is None:
        center = list(family.keys())[0]
    familytree = FamilyTree(family[center])
    return familytree

def make_node_texture(words, sex="Male"):
    f_path = "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc"
    f_size = 120
    i_size = 400
    font = ImageFont.truetype(f_path, f_size)
    if sex == "Male":
        color = (0, 127, 255)
    elif sex == "Female":
        color = (255, 0, 255)
    else:
        color = (255, 255, 255)
    img = Image.new("RGB", (i_size,i_size), color)
    draw = ImageDraw.Draw(img)
    f_y = (i_size-f_size)//2
    f_x = i_size//4 - f_size//2
    if str(words) != "nan":
        word = words[0]
        draw.text((f_x,f_y), word, font=font, fill=(255,255,255))
        f_x = i_size//4 * 3 - f_size//2
        draw.text((f_x,f_y), word, font=font, fill=(255,255,255))
    return img
        
def main():
    args = get_parser()
    out_path = Path(args.input).with_suffix(".pkl")
    df = pd.read_csv(args.input)
    check_csv(df)
    family = get_personal_data(df)
    familytree = build_family_tree(family, center=args.center)
    with open(str(out_path), "wb") as f:
        pickle.dump(familytree, f)
        
if __name__ == "__main__":
    main()