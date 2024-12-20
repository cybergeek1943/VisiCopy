# Project Proposal (VisiCopy)

> **Developers/Partners**: Isaac W. & Thomas R.
> 
> **Language**: Python
> 
> **License**: GPLv3
> 
> **Libraries and Frameworks**: PySide6, QFluentWidgets, subprocess, threading, json, pathlib, os, platform, copy, and PyInstaller and/or Nuitka (for deployment).
> 
> **Software Tools**: PyCharm, GitHub, VS Code, Obsidian, Draw.io, Lunacy, Qt RCC, and Qt Linguist, along with lupdate & lrelease.
> 
> **Assets**: I created many assets (such as icons) from scratch. I also use some of the smaller icons provided by QFluentWidgets. I then use Qt's RCC to convert icons and all other resources to Python byte strings. For language translation, I use Qt Linguist and Google Translate.


#### App Type & Option (BYOP)
We will be working on a software called VisiCopy. This software's primary function is to bring the power of powerful IT tools used for copying and migrating files and data to everyone. We will be working on specific sections of the UI, adding a few new features, improving codebase organization, and improving codebase documentation.


#### Description of **VisiCopy** (Visual Copy)
VisiCopy's primary purpose is to bring the power of IT tools to everyone by streamlining the process of copying and filtering files in a non-intimidating way. By providing users with an accessible, easily navigable, and self-explanatory user interface, VisiCopy aims to abstract away the complexities of multi-processed copying, backup software configuration (robocopy or rsync), and day-to-day workflow for those who often work with large files.

At its core, VisiCopy integrates advanced file copying utilities (robocopy and/or rsync) with an intuitive and self-explanatory user interface. VisiCopy includes additional custom features, such as batch processing and progress management + reports. Internally VisiCopy works by wrapping robocopy process instances managed by `Process(*settings_args)` objects so that all `STDOUT` and `STDERR` data is processed correctly and abstracted away so that easy manipulation and progress reports can be done using methods such as `processInstance.processProgress()`, `processInstance.currentFileProgress()`, `processInstance.stopProcess(force=True)`, etc. 


#### Features that we will introduce and improve
> **Previous overly ambitious goals**
> - Write detailed deployment documentation and create a step-by-step guide for working with resources such `.ts` language files and icon resources.
> - Make class diagrams for some of the major classes used.
> - Make an optimal user settings detector so that the initial settings are best suited for the computer that VisiCopy is running on... like optimized thread & process count limit.
> - Make a new source and destination UI for when the advanced user feature is enabled.


> **More realistic goals that we *were* able to complete**
> - (Mostly complete | Still needs a lot of cleanup) Make the codebase more modular by creating a custom UI package that unifies widgets from both PySide6 and QFluentWidgets into our own custom widgets package so that it's not the confusing mix-up that is currently going on.
> - (Complete | This just needs some more future work done on it to make it better) Improve the **Job Manager** by making the UI more intuitive.
> - (Complete | In the future, I will change the source and destination selection UI for advanced users) Add a new feature to the settings, such as a **super user** or **advanced user** switch. When the switch is off, many complex settings such as IPG (interpacket network gap), Database sparse states, and SMB compression will be hidden.
> - (Complete | This has significantly cleaned up the codebase) Add better support for saving settings and user data in the `AppData` folder for all platforms. Make the userdata versioned... that way different versions of VisiCopy have thier own userdata files.
> - Overall Codebase Improvements:
>   1. (Mostly Complete) Add docstrings for classes and methods.
>   2. (Some Comments were added) Add more comments to the code where necessary.
>   3. (Complete) Add doctests to functions where possible.
>   4. (Complete) Organize codebase and put into better categories.

 

#### Architecture
All the code is primarily Object-Oriented. The project is separated into several sections (directories), including: `core`, `main`, and `ui_lib`. The `core` contains most of the backend code for things such as instantiating processes, managing threads, and storing user data. The `ui_lib` provides some of the custom widgets used in VisiCopy. `main` is where the main UI is defined and also contains the `main.py` file (which is the entry point to the program).

**Below is a diagram (in progress) of the structure of our project:**
![Visicopy drawio](https://github.com/user-attachments/assets/70d59aa2-750d-4a5e-8df3-551339cec88f)



#### Basic UI sketch
This is an idea of the improved job manager with a list of the jobs. Each job entry will have buttons on it to change its settings, etc.:
![job_manager](https://github.com/user-attachments/assets/6546d89f-4968-400c-aae5-b120017b34e4)
This is the new **Advanced User** feature that will hide complex settings and improve UI for advanced users:
![advanced_user](https://github.com/user-attachments/assets/9ba8bd28-2a3a-457e-ae88-01d900adbdcf)


#### MVP
1. Improved **Job Manager**.
2. **Advanced User** feature should be implemented.


#### Interesting Challenges
- Making the VisiCopy project conducive to collaboration will be a challenge.
- It will be challenging to make the `.job` files editable because we will have to make the settings UI work for `.job` files. Currently, the settings UI is set up to only read from a single user data file. To make the settings UI code more flexible, we will need to rewrite the code that reads in the job file.
- It will be challenging to add the **Advanced User** feature to the settings UI Because it will require a small rewrite of the settings UI mini-framework I created. More specifically, we must write new code that manages which UI elements get hidden and which get shown based on a new `tags` attribute that is defined for UI elements in my settings UI framework.


#### Stretch Goals
1. (Easiest) Create a scheduler to run jobs at specified times in the background.
2. (Medium) Add support for **rsync** so that VisiCopy can have multi-platform support.
3. (ambitious, especially after adding support for **rsync**) Make a rigorous testing suite for most of VisiCopy's features.

There is a lot of testing and refining to be done on existing features, which will be done later. If the program could cause world peace, that’d be a huge win, but that’s EXTREMELY ambitious.
