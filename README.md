<p align="center">
  <img src="./img/GlaLogo.png" alt="UofG Logo" width="360">
</p>

# Jan-Hendrik Ewers MEng repo

## Install

### Step 1: AirSim
```bash
# Install UE 4.24 for AirSim
git clone -b 4.24 git@github.com/EpicGames/UnrealEngine.git /opt/UnrealEngine
cd /opt/UnrealEngine
./Setup.sh
./GenerateProjectFiles.sh
make

# Install AirSim
git clone git@github.com/Microsoft/AirSim.git /opt/AirSim
cd /opt/AirSim
./setup.sh
./build.sh
```



