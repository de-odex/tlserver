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

#show heading.where(level: 1): set text(
  font: "Nunito Sans 12pt",
  size: 21pt,
  weight: "bold",
)
#show heading.where(level: 1): set par(leading: 0.15em)
#show heading.where(level: 1): set block(
  above: 26pt,
  below: 10pt,
  sticky: true,
)

#show heading.where(level: 2): set text(
  font: "Nunito Sans 12pt",
  size: 18pt,
  weight: "bold",
)
#show heading.where(level: 2): set par(leading: 0.2em)
#show heading.where(level: 2): set block(
  above: 20pt,
  below: 8pt,
  sticky: true,
)

#show heading.where(level: 3): set text(
  font: "Nunito Sans 12pt",
  size: 16pt,
  weight: "bold",
)
#show heading.where(level: 3): set par(leading: 0.25em)
#show heading.where(level: 3): set block(
  above: 16pt,
  below: 7pt,
  sticky: true,
)

#show heading.where(level: 4): set text(
  font: "Nunito Sans 12pt",
  size: 14pt,
  weight: "bold",
)
#show heading.where(level: 4): set par(leading: 0.3em)
#show heading.where(level: 4): set block(
  above: 13pt,
  below: 6pt,
  sticky: true,
)

#show heading.where(level: 5): set text(
  font: "Nunito Sans 12pt",
  size: 12pt,
  weight: "bold",
)
#show heading.where(level: 5): set par(leading: 0.35em)
#show heading.where(level: 5): set block(
  above: 10pt,
  below: 6pt,
  sticky: true,
)

#show link: set text(fill: blue)
#show link: underline



////////////////////////////////////////////////////////////////////////////////
//                                   content
////////////////////////////////////////////////////////////////////////////////



// Simple, casual title
#align(center)[
  #text(
    font: "Nunito Sans 12pt",
    size: 32pt,
    weight: "bold",
  )[Hachimi Autotranslate Stories Guide]
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

#block(width: 100%, height: 1fr)[
  #figure(
    image("./images/image38.png"),
  )
]

#pagebreak()

= Sugoi Offline Guide (non-llm, kinda old)
== (Optional) If you have an NVIDIA GPU and want to use it to run translations:
Download the gpu installer #link("https://drive.google.com/file/d/1d6logK9H25Q5pqNmstLFUO2JeUCiwFW7/view?usp=sharing")[here] and extract the folder somewhere

#block[
  #figure(
    image("./images/image42.png"),
  )
]

Run the “run–install-cuda.bat” file and continue with the cmd popup instructions

== Main Guide
=== If using the sugoi install linked in this doc:
Navigate to your sugoi folder and run the “run.bat” file.

#block[
  #figure(
    image("./images/image34.png"),
  )
]

This should open up a command prompt and your server should be up and running.

#block[
  #figure(
    image("./images/image31.png"),
  )
]

=== If using any other version of sugoi (The below is using V14 as an example):
Navigate to your sugoi folder and run the “Sugoi-Translator-Toolkit (click here).bat” file.

#block[
  #figure(
    image("./images/image46.png"),
  )
]

It should open up a menu window. You want to look for “Translation Server Offline” and click on it.

#block[
  #figure(
    image("./images/image28.png"),
  )
]

It should open a command prompt and now your translation server is all good to go.

#block[
  #figure(
    image("./images/image31.png"),
  )
]

=== Unless your sugoi server is running at a different port, you should not need to do this step (This is specifically for every other version that’s not the V12 listed in the doc earlier) Skip to Next step if using the doc’s V12:

To find which port your server is running at, navigate to “Sugoi/Code” and look for the “User-Settings.json” file.

Open up the json file and look for an a list starting with [“Offline”]

Now look at the value set as "HTTP_port_number” and copy the value (in this case, 14366)

#block[
  #figure(
    image("./images/image44.png"),
  )
]

Close the json file and head to your umamusume/hachimi folder instead

#block[
  #figure(
    image("./images/image14.png"),
  )
]

Open the config.json file and find “sugoi_url”, it should be set as null by default

#block[
  #figure(
    image("./images/image27.png"),
  )
]

= Sugoi LLM Guide (LLM, really good, demanding)
Credits to Rika for the TLServer :3

== Prerequisites:
I will be using python 3.11 and uv to run this

Download python from #link("https://www.python.org/downloads/release/python-3110/")[here]
Make sure it is added to system path on install

Download #link("https://github.com/Kludex/uvicorn")[uv] by running “pip install uv” in your commandline

You will also need to have LM studio Installed (or any other openai compatible backends, etc)

Download from #link("https://lmstudio.ai/")[here] and it should be a straightforward setup

== Main Guide:
Pop over to this link #link("https://github.com/de-odex/tlserver")[here] and download the source as a zip, and extract it somewhere

Or run git clone https://github.com/de-odex/tlserver.git in your command line.

Alternatively download it from this #link("https://drive.google.com/file/d/1oewBsa-ToGFhqCplZyrkYnVH6covMy9y/view?usp=sharing")[link] for my exact personal setup

#block[
  #figure(
    image("./images/image9.png"),
  )
]

=== LM Studio Setup:
By default LM studio should be able to detect your GPU, but just in case it doesn’t we can set it up manually.

Open up LM studio and run through the setup if you haven’t already.

Navigate to the bottom right of your window and click on the settings icon (or press ctrl + ,)

#block[#figure(image("./images/image6.png"))]

From here you’ll be greeted by this window here. Navigate to the runtime tab.

#block[#figure(image("./images/image40.png"))]

You’ll be greeted by the list of runtimes.

#block[#figure(image("./images/image33.png"))]

For AMD GPUs, you should install the Vulkan engine (you can use ROCm but it lowkey runs like ass on windows).

#block[#figure(image("./images/image13.png"))]

For NVIDIA GPUs, you should pick CUDA

#block[#figure(image("./images/image7.png"))]

And then set your engine selection accordingly to which GPU you have.

#block[#figure(image("./images/image35.png"))]

Restart LM studio if it requires you to and continue with the next page

Make sure your LM studio mode is set to Power User or Developer beyond this point (Bottom Left)

#block[#figure(image("./images/image1.png"))]

=== Model Choices:
Now you will need to download a suitable model according to how much VRAM your GPU has. Here is my list of recommendations below

==== Best Model Hands Down (courtesy of mario :3):
Umamusume Story Translator (this changed my life)

==== Low VRAM (Less than 8gb):
Aya Expanse 8B
Shisa Ai v2 Qwen2.5 7B (probably the best one at this range)
Shisa Ai v2 Llama3.1 8B

==== Med VRAM (12gb):
Sugoi 14B Ultra (most meta option rn)

==== Higher VRAM (+16gb):
Note that these models are barely any better than sugoi
Shisa Ai v2 Mistral Nemo 12B
Shisa Ai v2 Unphi4 14B (my personal favourite to use)

Once you’ve decided on a model to use, pop over to the discover tab on LM Studio

#block[#figure(image("./images/image2.png"))]

You’ll be greeted with this window and you can search up your desired model and select the quantization for your VRAM size.

#block[#figure(image("./images/image37.png"))]

Technically you could download models using other sites like Huggingface etc but im too lazy to teach and write this wwww.

#block[#figure(image("./images/image23.png"))]
caption: Shisa Ai v2 Qwen2.5 7B as an example

You should probably listen to the LM studio recommendation for this, but you do you.

#block[#figure(image("./images/image32.png"))]

Slap the download button once happy and you should see the progress in your download tab.

#block[#figure(image("./images/image26.png"))]

=== Weirdass stuff you gotta do and check:
Pop over to the developer tab and click on the “select model to load search at the top”

#block[#figure(image("./images/image12.png"))]

Load your model of choice

#block[#figure(image("./images/image4.png"))]

Once loaded, check the model info on the right side of your tab

#block[#figure(image("./images/image29.png"))]

If the model formatting does not match “lm_studio/{modelname}” then we will need to move the model location around (weird LiteLLM shit). Otherwise, skip a couple pages to the TLServer Setup

Pop back into the “My Models” Tab and open your model directory in file explorer.

#block[#figure(image("./images/image10.png"))]

Ensure that you have an “lm_studio” folder.
If not, then just make a folder named “lm_studio”

#block[#figure(image("./images/image41.png"))]

You want to refer back to the model info to figure out which folder your model is in. In my case, since the model is “DevQuasar/shisa-ai.shisa-v2-qwen2.5-7b-GGUF” that means it will be found in the “DevQuasar” folder.

You should find your model in said folder

#block[#figure(image("./images/image8.png"))]

Make sure the model is unloaded (ejected) in LM Studio.

#block[#figure(image("./images/image51.png"))]

#block[#figure(image("./images/image22.png"))]

Move the model folder to the “lm_studio” folder from before.

#block[#figure(image("./images/image30.png"))]

Now load the model again in LM Studio and it should work and have the Model set to “lm_studio/{modelname}”

#block[#figure(image("./images/image25.png"))]

=== TLServer Setup

Pop over to where your extracted TLServer folder is

Open the “config.toml” file with some sort of text editor

#block[#figure(image("./images/image17.png"))]

By default it should have this written in it

#block[#figure(image("./images/image16.png"))]

If you’re using my personal version then you should see the following instead:

#block[#figure(image("./images/image15.png"))]

==== What the fuck is a config.toml file?
Basically you’re telling the server where your llm server is hosted at and how to use it.
As a general rule of thumb, at the bare minimum, your config.toml folder should be setup like below:

```toml
debug = true
root_port = 8080 # (only required if you downloaded via git or github)

[[translators]]
kind = "LLM"
model_name = "lm_studio/{modelname}"
api_server = "http://127.0.0.1:1234/v1"
api_key = "balls"
system_prompt = ""
```

===== Explanation of each variable
*api_server* - basically just where your LM studio instance is hosted, you can just set it to “http://127.0.0.1:1234/v1” and it should work

*model_name* - name of the model your using in LM studio, should be in the format “lm_studio/modelname”

*api_key* - This isn’t really used at all for LM studio but LiteLLM requires something in here for it to work, so just set it to whatever you want lol

*system_prompt* - Instructions on what the LLM is meant to do, how it translates text, and specific dictionary references. For lower end models, I would also highly suggest adding a dictionary so that the LLM doesn’t have a stroke trying to translate character names.

==== LLM Model Config Suggestions
If your suggested model config uses Top P, convert it into Min P:
1 – Top P = Min P

*Shisa V2 Variants:*
Running sampler sweeps, we found the models operate well across a variety of temperatures in most settings. For translation tasks specifically, we recommend a lower temperature (0.2) to increase accuracy. To prevent cross-lingual token leakage we recommend a min_p of 0.1.

*Sugoi 14B:*
- *Low Temperature*: `0.1`
- *Top K*: `40`
- *Min P*: `0.05`
- *Repetition Penalty*: `1.1`

==== Dictionary guide:
In your system prompt, you can specify a dictionary for the LLM to use on how to translate specific names or characters. This is highly important for LLMs with a lower parameter size.

You should run auto translation with a basic or no dictionary on a story once and reference the translations outputted in the command line to see what phrases or words might need a
dictionary.

Locations should be specified as a proper noun while names can just have the translation by itself. It is also a good idea to add every character’s name that appears in the story to the dictionary list as well.

For example, specifying how the LLM should translate a phrase or character’s name
```markdown
# Dictionary
Translate the below words accordingly
- "トレセン学園" as Tracen Academy and as a Proper Noun
- "ウマ娘" as "Uma Musume" and when referring to the game title as a common noun.
- "ダイワスカーレット" as "Daiwa Scarlet"
- "アストンマーチャン" as "Aston Machan" or if the shortened form is presented "アストンマ" translate it as "Machan", not marchan
```

Here is my system_prompt that I use. Feel free to adjust it accordingly
```markdown
# Role and Objective
You are a high-speed, silent, raw text translation API. Your sole purpose is to receive Japanese text and return the direct English translation, delivering accurate and culturally sensitive translations for the game "Uma Musume: Pretty Derby with maximum speed and efficiency.
- Demonstrate strong familiarity with the game's characters, terminology, and horse racing references.

**Core Directives:**
1.  **Prioritize Speed & Brevity:** Your primary goal is to respond with the minimum number of tokens required for an accurate translation.
2.  **Output Purity:** Your response MUST contain only the direct English translation. Nothing else.
3.  **Forbidden Content:** Do not include any explanations, reasoning, comments, apologies, or conversational filler. You are a tool, not an assistant.

**Example of Exact Format:**
User: こんにちは
Assistant: Hello

# Task Checklist
- Identify context, character names, and specialised terminology in the source text.
- Preserve original meaning, nuance, and tone in fluent English.
- Adapt jokes and cultural references for English audiences while retaining Japanese-specific humour if present.
- Maintain all Japanese honorifics, punctuation, placeholder tags, emoji, and emoticons exactly as in the source material.
- Use British English spelling and conventions exclusively.
- Translate cultural terms and onomatopoeia according to provided instructions or established guidelines.

# Instructions
- Output only the translated English text; do not include commentary, explanations, or extraneous information.
- Apply reasoning_effort = medium to ensure thorough but efficient handling of text complexity.
- Express the meaning and nuance of the source text faithfully; use colloquial expressions or slang only if they appear in the Japanese source.
- Appropriately adapt jokes and cultural references, retaining Japanese humour when present in the original.
- Preserve Japanese honorifics (e.g., -san, -sama, -kun) exactly as written.
- Retain original punctuation, including Japanese quotation marks, only if present in the source text.
- Translate ambiguous sentences in the most plausible manner; do not request clarification unless critical ambiguity prevents a reasonable translation.
- Match the register, formality, and regional speech patterns of characters in English.
- Use British English conventions consistently.
- Apply Hepburn romanisation with macrons for all relevant names and terms except honorifics.
- Romanise onomatopoeic expressions directly from the original.
- Reflect regional dialects and unique speech patterns, adapting them into English to preserve character voice (e.g., Kansai dialect, feminine speech).
- For culturally specific concepts without direct English equivalents, provide a brief parenthetical explanation inline (e.g., omiai (arranged meeting)).
- Preserve tags in angle brackets (e.g., `<username>`, `<chrname>`) and percent-encoded forms (e.g., `%a_h_pop1`, `%h_rank1`) exactly as given.
- Keep all emoji and emoticons unchanged.
- The Trainer character may be either male or female; unless specified in the source, translate Trainer dialogue and references using gender-neutral English.
- All horsegirls are female characters and should be referred to as "she/her" unless otherwise specified in the source.

# Dictionary
Translate the below words accordingly
- "トレセン学園" as Tracen Academy and as a Proper Noun
- "ウマ娘" as "Uma Musume" and when referring to the game title as a common noun.
# Output Format
Provide only the translated English text, formatted as plain text, without any added comments or notes.
Do not provide additional context or information for a given translation. Just only reply with the translation and nothing else
```

Once your “config.toml” file is set up, boot up cmd and cd to your TLServer directory.
Run the command “uv run tlserver”

#block[#figure(image("./images/image3.png"))]

If all goes well you should see something like this

#block[#figure(image("./images/image24.png"))]

= Getting Auto Translations to work in Hachimi
Open up your config.json file in “game_directory/hachimi”

== FOR SUGOI OFFLINE:
Now depending on what you copied earlier from the “User-Setting.json” file the link that you put in will be different. Replace Null with [“http://127.0.0.1:(COPIED-PORT)”]. In my case it will be [“http://127.0.0.1:14466”]

== For Sugoi LLM:
Set Sugoi_url to [“http://127.0.0.1:14368”]

== The Fun Part Begins Here:
Test if there are any issues with your sugoi server by opening up your game and navigating to the story tab

#block[#figure(image("./images/image45.png"))]

Open up hachimi gui and the config editor. Scroll down and tick “Auto Translate Stories”.

#block[#figure(image("./images/image36.png"))]

Press save

Now pick an untranslated story of your choice (for this guide I’ll be using Still In Love)

#block[#figure(image("./images/image48.png"))]

Click on an episode and view it

#block[#figure(image("./images/image19.png"))]

The game should freeze for a moment. Check your Sugoi Server Command Prompt and check if it has received any requests (it should look like the one below

#block[#figure(image("./images/image50.png"))]

Once your game unfreezes the sugoi server command prompt should look like this and your story should be translated now!

#block[#figure(image("./images/image43.png"))]

#block[#figure(image("./images/image49.png"))]

It is recommended that you only turn on auto translate stories for sections you actually care about, otherwise your game will turn into an unenjoyable laggy mess.

= Mobile? (Not really):
This isn’t really recommended right now due to the inability to use the hachimi gui on android

After setting up the server using the above steps, you can also use this for the android version of the game, as long as the server is on.

You will need to expose your localhost address hosting the sugoi server to your local network or expose it over the internet.

Local Network Method:

Idk how to do this, figure it out yourselves.

Cloudflared Method:

You have to do this step every time the sugoi server is started

(this also works if you wanna share your sugoi server with someone else)

Open command prompt and type in “winget install --id Cloudflare.cloudflared” and press enter

Follow installation instructions.

Type in “cloudflared tunnel --url http://127.0.0.1:(COPIED-PORT)” or “cloudflared tunnel --url http://127.0.0.1:14366” for offline sugoi if you haven’t changed any of your port settings.

Next cloudflare will spit out a link for you. Copy this one and place it somewhere for now.

#block[#figure(image("./images/image47.png"))]

Open your mobile device and navigate to android/media/umamusume/hachimi and open up the config.json file with a json editor.

Look for "auto_translate_stories" and set it from false to true

Next, set the “sugoi_url” from null to the cloudflare address generated from before. In my case it would be “https://doctor-maria-cigarettes-max.trycloudflare.com”

Save the config file and go to your game.

Your game may or may not be super laggy or stuttery. This is the main downside of using auto translate with the current state of hachimi on android.

Repeat the same testing step as the previous page and enjoy.


= heading
== heading
=== heading
==== heading
===== heading
a paragraph

another paragraph

= heading
a paragraph

another paragraph
== heading
a paragraph

another paragraph
=== heading
a paragraph

another paragraph
==== heading
a paragraph

another paragraph
===== heading
a paragraph

another paragraph
