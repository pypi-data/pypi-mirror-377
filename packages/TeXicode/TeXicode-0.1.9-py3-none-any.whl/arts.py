# bg = "░"
bg = " "
fraction = "╶─╴"

# from https://latexref.xyz/Math-functions.html
simple_leaf_commands = {
    " ", "_", "$", "{", "}", "#", "&",
    "arccos", "arcsin", "arctan", "arg", "bmod", "cos", "cosh", "cot", "coth",
    "csc", "deg", "det", "dim", "exp", "gcd", "hom", "inf", "ker", "lg", "lim",
    "liminf", "limsup", "ln", "log", "max", "min", "pmod",
    # "mod",  # \mod creates leading spaces, not simple
    "Pr", "sec", "sin", "sinh", "sup", "tan", "tanh", "%",
}

simple_symbols = """`!@#%*( )+-=[]|;:'",.<>/?""" # note whitespace is in there

special_symbols = {
    "~": " ",
    "&": "",
}

alphabets = {
    "normal":     "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "serif_it":   "𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧",
    "serif_bld":  "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳",
    "serif_itbd": "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛",
    "sans":       "𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓",
    "sans_it":    "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻",
    "sans_bld":   "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇",
    "sans_itbd":  "𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯",
    "mono":       "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣",
    "cali_bld":   "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃",
    "frak_bld":   "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟",
    "double":     "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫",
}

font = {
    "mathrm":     alphabets["normal"],
    "mathbf":     alphabets["serif_bld"],
    "mathsf":     alphabets["sans"],
    "mathtt":     alphabets["mono"],
    "mathit":     alphabets["serif_it"],
    "mathnormal": alphabets["serif_it"],
    "mathcal":    alphabets["cali_bld"],
    "mathfrak":   alphabets["frak_bld"],
    "mathbb":     alphabets["double"],
    "mathscr":    alphabets["cali_bld"],
    "text":       alphabets["normal"]
}

multi_line_leaf_commands = {
    "sum":
    (["┰─╴",
      "▐╸ ",
      "┸─╴",], 1),
    # "sum":
    # (["┌──",
    #   "🮥  ",
    #   "└──",], 1),
    "prod":
    (["┰─┰",
      "┃ ┃",
      "┸ ┸",], 1),
    "int":
    (["⌠",
      "⎮",
      "⌡",], 1),
    "iint":
    (["⌠⌠",
      "⎮⎪",
      "⌡⌡",], 1),
    "iiint":
    (["⌠⌠⌠",
      "⎮⎮⎮",
      "⌡⌡⌡",], 1),
    "idotsint":
    (["⌠ ⌠",
      "⎮⋯⎮",
      "⌡ ⌡",], 1),
    "oint":
    ([" ⌠ ",
      "╶╪╴",
      " ⌡ ",], 1),
    "oiint":
    ([" ⌠⌠ ",
      "╶╪╪╴",
      " ⌡⌡ ",], 1),
    "oiiint":
    ([" ⌠⌠⌠ ",
      "╺╪╪╪╸",
      " ⌡⌡⌡ ",], 1),
}

square_root = {
    "top_bar": "─",
    "top_tail": "╴",
    "top_angle": " ┌",
    "left_bar":  " │",
    "btm_angle": "╰┘",

    # "top_bar": "─",
    # "top_tail": "╴",
    # "top_angle": " ┌",
    # "left_bar":  " │",
    # "btm_angle": "╲𜸙",

    # "top_bar": "─",
    # "top_tail": "╴",
    # "top_angle": " ┌",
    # "left_bar":  " │",
    # "btm_angle": "🯓🯗",

    # "top_bar": "─",
    # "top_tail": "╴",
    # "top_angle": " ┌",
    # "left_bar":  " │",
    # "btm_angle": "╲⎦", #⌡

    # "top_bar": "▔",
    # "top_tail": "▔",
    # "top_angle": "▕▔",
    # "left_bar":  " ▏",
    # "btm_angle": "╲▏",

    # "top_bar": "─",
    # "top_tail": "╴",
    # "top_angle": "𜺯─",
    # "left_bar":  " ▏",
    # "btm_angle": "╲▏",

    # "top_bar": "─",
    # "top_tail": "╴",
    # "top_angle": " 🯐",
    # "left_bar":  " ▏",
    # "btm_angle": "╲▏",
}

unicode_scripts = {
    " ": "  ", "0": "⁰₀", "1": "¹₁", "2": "²₂", "3": "³₃", "4": "⁴₄",
    "5": "⁵₅", "6": "⁶₆", "7": "⁷₇", "8": "⁸₈", "9": "⁹₉",
    "+": "⁺₊", "-": "⁻₋", "=": "⁼₌", "!": "ꜝ ", "(": "⁽₍", ")": "⁾₎",
    "A": "ᴬ ", "a": "ᵃₐ", "B": "ᴮ𞁓", "b": "ᵇ ", "C": "ᶜ𞁞", "c": "ᶜ𞁞",
    "D": "ᴰ ", "d": "ᵈ ", "E": "ᴱ ", "e": "ᵉₑ", "F": "ᶠ ", "f": "ᶠ ",
    "G": "ᴳ ", "g": "ᵍ ", "H": "ᴴ ", "h": "ʰₕ", "I": "ᴵᶦ", "i": "ⁱᵢ",
    "J": "ᴶ ", "j": "ʲⱼ", "K": "ᴷ𞁚", "k": "ᵏₖ", "L": "ᴸ ", "l": "ˡₗ",
    "M": "ᴹ ", "m": "ᵐₘ", "N": "ᴺ ", "n": "ⁿₙ", "O": "ᴼ𞁜", "o": "ᵒₒ",
    "P": "ᴾ ", "p": "ᵖₚ", "Q": "ꟴ ", "q": "𐞥 ", "R": "ᴿ ", "r": "ʳᵣ",
    "S": "ˢₛ", "s": "ˢₛ", "T": "ᵀ ", "t": "ᵗₜ", "U": "ᵁ ", "u": "ᵘᵤ",
    "V": "ⱽᵥ", "v": "ᵛᵥ", "W": "ᵂ ", "w": "ʷ ", "X": "ˣₓ", "x": "ˣₓ",
    "Y": "𐞲ᵧ", "y": "ʸᵧ", "Z": "ᶻ ", "z": "ᶻ ",
    "α": "ᵅ ", "β": "ᵝᵦ", "γ": "ᵞᵧ", "δ": "ᵟ ", "ε": "ᵋ ", "θ": "ᶿ ",
    "ι": "ᶥ ", "ϕ": "ᶲ ", "φ": "ᵠᵩ", "χ": "ᵡᵪ", "ρ": " ᵨ",
    "/": "ᐟ ",
    # ᐞᐟᐠᐡᐢᐣᐥᐦᐨᐩᑉᑊᔆᕀᕁᙾ
}

delimiter = {
    "sgl": "(){}[]⌊⌋⌈⌉||‖‖",
    "top": "╭╮╭╮┌┐╷╷┌┐╷╷║║",
    "ctr": "││┥┝││││││││║║",
    "fil": "││││││││││││║║",
    "btm": "╰╯╰╯└┘└┘╵╵╵╵║║",
}


delimiter = {
    "sgl": "(){}[]⌊⌋⌈⌉||‖‖",
    "top": "⎛⎞⎧⎫⎡⎤⎢⎥⎡⎤⎟⎜║║",
    "ctr": "⎜⎟⎨⎬⎢⎥⎢⎥⎢⎥⎟⎜║║",
    "fil": "⎜⎟⎪⎪⎢⎥⎢⎥⎢⎥⎟⎜║║",
    "btm": "⎝⎠⎩⎭⎣⎦⎣⎦⎢⎥⎟⎜║║",
}

# delimiter = {
#     "left":  {"sgl": "([{|",
#               "top": "╭┌╭│",
#               "ctr": "││┥│",
#               "fil": "││││",
#               "btm": "╰└╰│"},
#     "right": {"sgl": ")]}|",
#               "top": "╮┐╮│",
#               "ctr": "││┝│",
#               "fil": "││││",
#               "btm": "╯┘╯│"},
# }
