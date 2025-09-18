<p align="center"><h1 align="center"> {{ project_name_upper }} PROJECT </h1></p>
<p align="center">
	<em><code>Python Game/Graphics project with Xodex.
</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/username/{{ project_name }}?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/username/{{ project_name }}?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/username/{{ project_name }}?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/username/{{ project_name }}?style=default&color=0080ff" alt="repo-language-count">
</p>

<details><summary>Table of Contents</summary>

- [📍 Overview](#📍-overview)
- [🚀 Features](#🚀-features)
- [🎮 Gameplay](#🎮-gameplay)
- [🕹️ Controls](#🕹️-controls)
- [📁 Project Structure](#📁-project-structure)
- [📌 Getting Started](#📌-getting-started)
  - [☑️ Prerequisites](#☑️-prerequisites)
  - [⚙️ Installation](#⚙️-installation)
  - [🤖 Usage](#🤖-usage)
- [🔰 Contributing](#🔰-contributing)
- [🙌 Acknowledgments](#🙌-acknowledgments)
- [📚 References](#📚-references)
- [📝 License](#📝-license)

</details>

## 📍 Overview

>This project is built using Xodex.


### 🚀 Features
- **Game Controls:** Easy-to-use keyboard controls.
- **Score System:** Earn points and advance through levels.
- **Pause/Resume:** Players can pause the game at any moment and resume where they left off.
- **Collision Detection:** Ensures a realistic gameplay experience.
- **Music and Sound Effects:** Enhances gameplay with engaging audio.


### 🎮 Gameplay

The objective is to place the tetrominoes to create complete lines, which will then be cleared from the board.
The game ends when the Tetris playfield is filled.

- Use the arrow keys to control basic controls.
- The game features a main menu where you can start the game or exit.
- You can pause the game by pressing the designated pause key (to be defined in settings).

### 🕹️ Controls

- **A** / **Left Arrow** : Move Left
- **D** / **Right Arrow** : Move Right
- **S** / **Down Arrow** : Move Down
- **W** / **Up Arrow** : Move Up
- **Space** : Pause/Resume Game


## 📁 Project Structure
```
{{ project_name }}
├── {{ project_name }}
│   ├── __init__.py
│   ├── __main__.py        # Entry point to run project as module.
│   ├── settings.py        # Project Configurations and Settings. 
│   ├── objects            # Directory to Create and Register Objects.
│   │   └── __init__.py    # To Register Project Game Objects.   
│   └── scenes             # Directory to create and register Scenes.
│       └── __init__.py    # To Register Project Game Scenes.
├── manage.py              # Project Management utilities. 
├── requirements.txt       # Project dependencies.
├── .gitignore             # Files to ignore in Git.
├── LICENSE                # Project License.
└── README.md              # Project Documentation.
```

## 📌 Getting Started

#### ☑️ Prerequisites

| Module                                                                | Detail                      | Minimum Version                             |
|-------------------------------------------------------------------------|--------------------------------|---------------------------------------------|
| [Xodex](https://github.com/djoezeke/xodex/)                                        | Game Engine            | {{ xodex_version }}                                         |
| [Pygame](https://github.com/pygame/pygame/)        | Cross-platform Game framework.                        | {{ pygame_version }}                                       |
| [PygameUI](https://github.com/djoezeke/pygameui/) ( Optional)                                      | Project Graphical User Interface.            | {{ pygameui_version }}                                          |

🧰 Additional Tools

- [Git](https://git-scm.com/) – (Optional) Version control and submodule/dependency management

### ⚙️ Installation
To run the {{ project_name }} game, follow these steps:

1. **Clone the repository**:
```sh
   git clone https://github.com/username/{{ project_name }}
   cd {{ project_name }}
```

2. **Install dependencies**:
   Ensure you have Python installed. You may need to install additional libraries depending on your game implementation.

```sh
   pip install -r requirements.txt
```

3. **Run the game**:
   Execute the following command:
```sh
   python manage.py run
```
or:
```sh
   python -m {{ project_name }}
```

4. **Building the game**:
To build the game executable using PyInstaller, run:
```sh
python manage.py build
```
This will create a standalone executable in the `dist` directory.

5. **Distributing the game**:
After building the game, you can distribute the executable found in the `dist` folder. Users can run the game without needing to install Python or any dependencies.


## 🔰 Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the game.

- **💬 [Join the Discussions](https://github.com/username/{{ project_name }}/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/username/{{ project_name }}/issues)**: Submit bugs found or log feature requests for the `{{ project_name }}` project.
- **💡 [Submit Pull Requests](https://github.com/username/{{ project_name }}/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone --recursive https://github.com/username/{{ project_name }}
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/username/{{ project_name }}/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=username/{{ project_name }}">
   </a>
</p>
</details>


## 🙌 Acknowledgments

We would like to express our gratitude to the following projects and individuals whose work made this project possible:

- [Xodex](https://github.com/djoezeke/xodex/) – for core Game Design.
- [PygameUI](https://github.com/djoezeke/pygameui/) – for the game Graphical User Interface.
- [Pygame](https://github.com/pygame/pygame/) – for providing a robust, cross-platform game framework.
- The open-source community for their invaluable libraries, tutorials, and support.
- Special thanks to all contributors, testers, and users who provided feedback and suggestions.

## 📚 References

- **Intresting:**
  - [PyGame](https://www.pygame.org/)
  - [Pygame CE](https://pyga.me/)

- **Learning Resources:**
  - [Xodex Example Projects](https://github.com/djoezeke/xodex_examples/)
  - [Official Pygame Tutorial](https://www.pygame.org/)
  - [Offical Pygame CE Tutorial](https://pyga.me/)

## 📝 License

This project is protected under the [MIT](LICENSE) License. 
For more details, refer to the [LICENSE](LICENSE) file.
