#import "@preview/basic-report:0.5.0": basic-report
#import "@preview/alertoni:1.0.0" as at
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *

// Codeblocks

#show: codly-init.with()

#codly(
  languages: codly-languages,
  number-format: none,
  display-icon: false,
  display-name: false,
)

// Keep Japanese glyphs in code monospaced and legible.
#show raw: set text(font: ("Fantasque Sans Mono", "Noto Sans Mono CJK JP"))
#show raw.where(block: false): set text(size: 1.2em)
#show raw.where(block: false): it => box(
  fill: luma(230),
  radius: 2pt,
  inset: (x: 1.5pt, y: 0pt),
  outset: (x: 0pt, y: 2.5pt),
)[#it]

// Page layout

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
  font: ("Atkinson Hyperlegible Next", "Noto Sans CJK JP"),
  size: 10.5pt,
)

#set par(
  leading: 0.55em,
  justify: false,
)

// Headings

#set heading(numbering: none)
#show heading: set text(
  font: ("Nunito Sans 12pt", "Noto Sans CJK JP"),
)

#show heading.where(level: 1): set text(
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
  size: 12pt,
  weight: "bold",
)
#show heading.where(level: 5): set par(leading: 0.35em)
#show heading.where(level: 5): set block(
  above: 10pt,
  below: 6pt,
  sticky: true,
)

// Links

#show link: set text(fill: blue)
#show link: underline

// Callouts

#let callout = at.callout.with(style: "quarto")

// "Continuation on the next page"

#show enum: it => [
  #metadata("start") <enum-boundary>
  #it
  #metadata("end") <enum-boundary>
]

#set page(
  paper: "a4",
  margin: (
    x: 20mm,
    y: 20mm,
  ),
  numbering: "1",

  footer: context {
    let current-page = here().page()
    let boundaries = query(<enum-boundary>)

    let continuing = boundaries
      .chunks(2)
      .any(pair => {
        (
          pair.len() == 2
            and pair.first().location().page() <= current-page
            and pair.last().location().page() > current-page
        )
      })

    let banner = if continuing {
      block(
        width: 100%,
        height: 20pt,
        //fill: rgb("#FFE08A"),
        //stroke: 1pt + rgb("#B56A00"),
        fill: rgb("#DCEEFF"),
        stroke: 1pt + rgb("#3976A8"),
        radius: 4pt,
        //inset: 5pt,
        align(center + horizon)[
          #text(
            size: 10.5pt,
            weight: "bold",
            //fill: rgb("#7A3E00"),
          )[↓ STEPS CONTINUE ON THE NEXT PAGE ↓]
        ],
      )
    } else {
      // Keep footer height stable on pages without the banner.
      block(width: 100%, height: 20pt)
    }

    grid(
      columns: (1fr,),
      rows: (20pt, auto),
      row-gutter: 4pt,
      banner,
      align(center, counter(page).display("1")),
    )
  },
)


////////////////////////////////////////////////////////////////////////////////
//                                   content
////////////////////////////////////////////////////////////////////////////////



// Simple, casual title
#align(center)[
  #text(
    font: ("Nunito Sans 12pt", "Noto Sans CJK JP"),
    size: 32pt,
    weight: "bold",
  )[Hachimi Autotranslate Stories Guide]
  #v(-2.4em)
  #text(size: 14pt)[TLServer]
  #v(-0.8em)
  #text(size: 10.5pt)[Written by #strike[Spoot :3] Rika]
]

#v(2em)

#callout(type: "info")[
  Hi! This is my (Rika's) guide for setting up TLServer. It's mainly adapted from Spoot's guide.

  I will try to keep this updated, but if you accessed the file *directly* from a link, then you *won't* see updates.

  Make sure you accessed this through a *folder* link.
]

#callout(type: "warning")[
  This requires a half decent device to run (think at least 4 GB video RAM), as this is run locally using your PC’s CPU/GPU (depending on your choice). This will also cause your game to freeze/lag a lot more.
]

This technically is meant only for PC, but you can get it to work on a mobile device by running Sugoi locally on a PC and exposing the Sugoi server address either on your local network or the internet so that your mobile device can connect to the Sugoi server.

For this guide, I will be using a trimmed down #link("https://lunatranslator.org/Resource/translate/sugoi_V12.1_683043.7z")[Sugoi V12.1] with only the translation server functionality, called TLServer.
You can try to use your own version, but it is not guaranteed to work, or if the instructions will be the same at all (though, I tested this on the latest V14 and it also works).

#block(width: 100%, height: 1fr)[
  #figure(
    image("./images/PlbyG6zhQ0WbjOhp.png"),
  )
]

#pagebreak(weak: true)
= Prerequisites

This guide assumes Windows; For Mac and Linux users, it's mainly the same steps.

+ #block(breakable: false)[
    I will be using `uv` to run TLServer.
    To install #link("https://docs.astral.sh/uv/")[uv], run `winget install --id=astral-sh.uv -e` in a command prompt.

    #callout(type: "warning")[
      If you, for some reason, cannot use `winget`, you can follow the installation instructions in #link("https://docs.astral.sh/uv/getting-started/installation/#installation-methods")[this link].

      Please be warned that using this method is more dangerous, as you are running a script that may be hijacked and cause damage to your system.

      The `winget` method is a bit safer than this method.
    ]
  ]

+ You will also need to install #link("https://lmstudio.ai/")[LM Studio] (or any other OpenAI compatible backends, etc).

+ #block(breakable: false)[
    Then, download TLServer by opening this link #link("https://github.com/de-odex/tlserver")[here], downloading the source as a zip, and extracting it somewhere.

    You can also instead run `git clone https://github.com/de-odex/tlserver.git` in your command line.

    #block(width: 100%)[
      #figure(
        image("./images/image9.png"),
      )
    ]
  ]

#pagebreak(weak: true)
= LM Studio Setup

By default, LM Studio should be able to detect your GPU, but just in case it doesn’t, we can set it up manually.

+ Open up LM Studio and run through the setup if you haven’t already.

+ #block(breakable: false)[
    Navigate to the bottom left of your window and click on the settings icon (or press `ctrl + ,`).

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_045614.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    From here you’ll be greeted by this window here. Navigate to the runtime tab.

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_045759_LM Studio.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    You’ll be greeted by the list of runtimes.

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_045737_LM Studio.png"),
      )
    ]
  ]

  - #block(breakable: false)[
      For AMD GPUs, you should install the Vulkan engine (you can use ROCm but it lowkey runs like ass on Windows).

      #block(width: 100%)[
        #figure(
          image("./images/Screenshot_20260828_050104.png"),
        )
      ]
    ]

  - #block(breakable: false)[
      For NVIDIA GPUs, you should pick CUDA.
      If you get slow LLM generation (< 10 tokens per second), try choosing the one that only says "CUDA" and not "CUDA 12".

      #block(width: 100%)[
        #figure(
          image("./images/Screenshot_20260828_045853.png"),
        )
      ]
    ]

+ #block(breakable: false)[
    Then set your engine selection accordingly to which GPU you have.

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_050149.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    Restart LM Studio if it requires you to, and continue with the next page.

    Make sure your LM Studio mode is set to Developer beyond this point (Settings > Developer > Developer Mode).

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_050238.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    Now you will need to download a suitable model according to how much VRAM your GPU has.

    These are the models I (Rika) recommend:
    - If you have 16 or more GB VRAM: *Hy MT2 7B*, GGUF format
    - If you have 8 or more GB VRAM: *Hy MT2 1.8B*, GGUF format
    - If you have 4 or less GB VRAM: *Good luck.* Try loading Hy MT2 1.8B and see if the `Q4_K_M` quantisation fits; we'll elaborate on that in the next step.

    Spoot recommended these models; they're a couple of years old and may perform worse than the ones I recommend:

    #text(fill: black.lighten(50%))[
      *Best Model Hands Down (courtesy of Mario :3)*
      - Umamusume Story Translator (this changed my life)

      *Low VRAM (Less than 8gb)*
      - Aya Expanse 8B
      - Shisa Ai v2 Qwen2.5 7B (probably the best one at this range)
      - Shisa Ai v2 Llama3.1 8B

      *Med VRAM (12gb)*
      - Sugoi 14B Ultra (most meta option rn)

      *Higher VRAM (+16gb)* \
      #callout(type: "info", style: "compact")[
        Note that these models are barely any better than Sugoi.
      ]
      - Shisa Ai v2 Mistral Nemo 12B
      - Shisa Ai v2 Unphi4 14B (my personal favourite to use)
    ]
  ]

+ #block(breakable: false)[
    Once you’ve decided on a model to use, pop over to the Model Search tab on LM Studio.

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_051217.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    You’ll be greeted with this window; you can search up your desired model and select the quantisation for your VRAM size.

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_051329_LM Studio.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    Technically, you could download models using other sites like Huggingface, etc. but I'm too lazy to teach and write this wwww.

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_051408_LM Studio.png"),
        caption: "Hy-MT2 as an example",
      )
    ]
  ]

+ #block(breakable: false)[
    You should probably listen to the LM Studio recommendation for which model to choose, but you do you.

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_051556.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    Slap the download button once you're happy and you should see the progress in your download tab.

    #block(width: 100%)[
      #figure(
        image("./images/Screenshot_20260828_051633.png"),
      )
    ]
  ]

#pagebreak(weak: true)
= TLServer Setup <tlsrv-setup>

+ #block(breakable: false)[
    Pop over to where your extracted TLServer folder is.

    Open the `config.toml` file with some sort of text editor.

    #block(width: 100%)[
      #figure(
        image("./images/image17.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    By default it should have this written in it:

    #block(width: 100%)[
      #figure(
        image("./images/image16.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    If you’re using my personal version then you should see the following instead:

    #block(width: 100%)[
      #figure(
        image("./images/image15.png"),
      )
    ]
  ]

== What the fuck is a config.toml file?

#block(breakable: false)[
  Basically you’re telling the server where your LLM server is hosted at and how to use it.
  As a general rule of thumb, at the bare minimum, your config.toml folder should be setup like below:

  ```toml
  debug = true
  root_port = 8080

  [[translators]]
  kind = "LLM"
  model_name = "lm_studio/{your model's name}"
  # api_server = "http://127.0.0.1:1234/v1"
  ```
]

=== Explanation of each variable
*api_server* - Basically just where your LM Studio instance is hosted. If you changed this setting in LM Studio, you have to uncomment and set it here too. Otherwise, don't change anything.

#block(breakable: false)[
  *model_name* - Name of the model you're using in LM Studio. Should be in the format “lm_studio/{your model's name}”. You can find your model name in this screen:

  #block(width: 100%)[
    #figure(
      image("./images/Screenshot_20260828_045043.png"),
      caption: [In this example, the `model_name` should be `lm_studio/tencent/Hy-MT2-7B-GGUF`],
    )
  ]
]

*system_prompt* - Instructions on what the LLM is meant to do, how it translates text, and specific dictionary references. You only need to set it if you're not using my config, or if you know what you're doing.

== LLM Model Config Suggestions

#block(breakable: false)[
  //If your suggested model config uses Top P, convert it into Min P:
  //$ 1 – "Top P" = "Min P" $

  For my recommended models:

  *Hy MT2*:
  All variants can use the same settings:
  - *Temperature*: `0.7`
  - *Top K*: `20`
  - *Top P*: ticked on, `0.6`
  - *Min P*: ticked off
  - *Repetition Penalty*: ticked on, 1.05

  I also recommend setting these:
  - *Context Length*: As much as you can fit. I have a 16 GB GPU that can fit `32768` tokens, using up 2 GB extra VRAM. `8192` might be a good starting value, increase to `16384` if you can.

  For Spoot's recommended models:

  #text(fill: black.lighten(50%))[
    *Shisa V2 Variants:*
    Running sampler sweeps, we found the models operate well across a variety of temperatures in most settings. For translation tasks specifically, we recommend a lower temperature (0.2) to increase accuracy. To prevent cross-lingual token leakage we recommend a min_p of 0.1.
    - *Temperature*: `0.2`
    - *Min P*: `0.1`

    *Sugoi 14B:*
    - *Temperature*: `0.1`
    - *Top K*: `40`
    - *Min P*: `0.05`
    - *Repetition Penalty*: `1.1`
  ]
]

== Dictionary guide:
#callout(type: "warning")[
  TODO
]
In your system prompt, you can specify a dictionary for the LLM to use on how to translate specific names or characters. This is highly important for LLMs with a lower parameter size.

You should run auto translation with a basic or no dictionary on a story once and reference the translations outputted in the command line to see what phrases or words might need a
dictionary.

Locations should be specified as a proper noun while names can just have the translation by itself. It is also a good idea to add every character’s name that appears in the story to the dictionary list as well.

For example, specifying how the LLM should translate a phrase or character’s name:
```markdown
# Dictionary
Translate the below words accordingly
- "トレセン学園" as Tracen Academy and as a Proper Noun
- "ウマ娘" as "Uma Musume" and when referring to the game title as a common noun.
- "ダイワスカーレット" as "Daiwa Scarlet"
- "アストンマーチャン" as "Aston Machan" or if the shortened form is presented "アストンマ" translate it as "Machan", not marchan
```

The `system_prompt` I use for translating can be found in the shared folder. Feel free to adjust it accordingly.

4. #block(breakable: false)[
    Once your `config.toml` file is set up, boot up Command Prompt and `cd` to your TLServer directory.

    Run the command `uv run tlserver`.

    #block(width: 100%)[
      #figure(
        image("./images/image3.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    If all goes well you should see something like this:

    #block(width: 100%)[
      #figure(
        image("./images/image24.png"),
      )
    ]
  ]

#pagebreak(weak: true)
= Hachimi Setup
+ Open up your `config.json` file in `Umamusume/hachimi`.

+ Set `Sugoi_url` to `[“http://127.0.0.1:14368”]`.

+ #block(breakable: false)[
    Test if there are any issues with your Sugoi server by opening up your game and navigating to the story tab.

    #block(width: 100%)[
      #figure(
        image("./images/image45.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    Open up Hachimi's GUI and the config editor. Scroll down and tick “Auto Translate Stories”.

    #block(width: 100%)[
      #figure(
        image("./images/image36.png"),
      )
    ]
  ]

+ Press save.

+ #block(breakable: false)[
    Now pick an untranslated story of your choice (for this guide I’ll be using Still In Love).

    #block(width: 100%)[
      #figure(
        image("./images/image48.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    Click on an episode and view it.

    #block(width: 100%)[
      #figure(
        image("./images/image19.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    The game should freeze for a moment. Check your Sugoi Server's command prompt and check if it has received any requests (it should look like the one below).

    #block(width: 100%)[
      #figure(
        image("./images/image50.png"),
      )
    ]
  ]

+ #block(breakable: false)[
    Once your game unfreezes, the Sugoi server command prompt should look like this.
    Your story should be translated now!

    #block(width: 100%)[
      #figure(
        image("./images/image43.png"),
      )
    ]

    #block(width: 100%)[
      #figure(
        image("./images/image49.png"),
      )
    ]

    #callout(type: "info")[
      It is recommended that you only turn on auto translate stories for sections you actually care about, otherwise your game will turn into an unenjoyable laggy mess.
    ]
  ]

#pagebreak(weak: true)
= Mobile? (Not really)

This isn’t really recommended right now due to the inability to use the Hachimi GUI on Android.

After setting up the server using the above steps, you can also use this for the Android version of the game, as long as the server is on.

You will need to expose your localhost address hosting the Sugoi server to your local network or expose it over the internet.

== Local Network Method:

IDK how to do this, figure it out yourselves.

== Cloudflared Method:

You have to do this step every time the Sugoi server is started.

(this also works if you wanna share your Sugoi server with someone else).

Open Command Prompt and type in `winget install --id Cloudflare.cloudflared` and press enter.

Follow installation instructions.

Type in `cloudflared tunnel --url http://127.0.0.1:(COPIED-PORT)` or `cloudflared tunnel --url http://127.0.0.1:14366` for offline Sugoi, if you haven’t changed any of your port settings.

Next, Cloudflare will spit out a link for you. Copy this one and place it somewhere for now.

#block(width: 100%)[
  #figure(
    image("./images/image47.png"),
  )
]

Open your mobile device and navigate to `android/media/umamusume/hachimi` and open up the config.json file with a JSON editor.

Look for `auto_translate_stories` and set it from `false` to `true`.

Next, set the `sugoi_url` from `null` to the cloudflare address generated from before. In my case it would be “https://doctor-maria-cigarettes-max.trycloudflare.com”.

Save the config file and go to your game.

Your game may or may not be super laggy or stuttery. This is the main downside of using auto translate with the current state of Hachimi on Android.

Repeat the same testing step as the previous page and enjoy.
