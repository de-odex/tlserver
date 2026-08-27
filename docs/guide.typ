#import "@preview/basic-report:0.5.0": basic-report
#import "@preview/alertoni:1.0.0" as at

#set document(
  title: [Hachimi Autotranslate Stories Guide],
)

#set page(
  paper: "a4",
  margin: (
    x: 20mm,
    y: 20mm,
  ),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "Atkinson Hyperlegible Next",
  size: 10.5pt,
)

#set par(
  leading: 0.55em,
  justify: false,
)

#set heading(numbering: none)

#show heading.where(level: 1): it => block(
  above: 2em,
  below: 0.65em,
)[
  #set text(font: "Nunito Sans 12pt", size: 21pt, weight: "bold")
  #it.body
]

#show heading.where(level: 2): it => block(
  above: 1.5em,
  below: 0.5em,
)[
  #set text(font: "Nunito Sans 12pt", size: 16pt, weight: "bold")
  #it.body
]

#show heading.where(level: 3): it => block(
  above: 1.15em,
  below: 0.4em,
)[
  #set text(font: "Nunito Sans 12pt", size: 13pt, weight: "bold")
  #it.body
]

#show heading.where(level: 4): it => block(
  above: 0.95em,
  below: 0.35em,
)[
  #set text(font: "Nunito Sans 12pt", size: 11.5pt, weight: "bold")
  #it.body
]

#show heading.where(level: 5): it => block(
  above: 0.8em,
  below: 0.3em,
)[
  #set text(font: "Nunito Sans 12pt", size: 10.5pt, weight: "bold")
  #it.body
]

#show link: set text(fill: blue)
#show link: underline



////////////////////////////////////////////////////////////////////////////////
//                                   content
////////////////////////////////////////////////////////////////////////////////



// Simple, casual title
#align(center)[
  #text(font: "Nunito Sans 12pt", size: 32pt, weight: "bold")[Hachimi Autotranslate Stories Guide]
  #v(-2em)
  #text(size: 14pt)[Sugoi Offline Translator | tlserver]
  #v(-0.8em)
  #text(size: 10.5pt)[Written by Spoot :3]
]

#v(2em)

#at.callout(type: "warning", style: "quarto")[
  This requires a half decent device to run, as this is run locally using your pc’s CPU/GPU (depending on your choice). This will also cause your game to freeze/lag a lot more.
]

This technically is meant only for pc, but you can get it to work on a mobile device by running sugoi locally on a pc and exposing the sugoi server address either on your local network or the internet so that your mobile device can connect to the sugoi server.

For this guide I will be using a trimmed down #link("https://lunatranslator.org/Resource/translate/Sugoi_V12.1_683043.7z")[Sugoi V12.1] with only the translation server functionality. You can try to use your own version but it is not guaranteed to work or if the instructions will be the same at all (Tho, I tested this on the latest V14 and it also works).

#text(size: 3em, weight: "bold")[
  AUTOTL VIA THIS METHOD IS BROKEN ON V0.26, PLEASE DOWNGRADE TO v0.25.4 BEFORE PROCEEDING
]

#pagebreak()

= Sugoi Offline Guide (non-llm, kinda old)
== (Optional) If you have an NVIDIA GPU and want to use it to run translations:
Download the gpu installer #link("https://drive.google.com/file/d/1d6logK9H25Q5pqNmstLFUO2JeUCiwFW7/view?usp=sharing")[here] and extract the folder somewhere


= test
== test
=== test
==== test
===== test
hello

= test
hello
== test
hello
=== test
hello
==== test
hello
===== test
hello

more body text
