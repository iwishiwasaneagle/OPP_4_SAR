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

# Install anaconda and dependencies for airsim on arch https://github.com/microsoft/AirSim/issues/2708#issuecomment-632235479
# IGNORE IF USING UBUNTU: Comment out any "sudo apt-get" in setup.sh
curl https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh  | bash # Place in /opt/anaconda3 when asked 
conda create --name airsim
conda activate airsim
conda install -c conda-forge boost clang=8.0.1 libcxx=8.0.1
sudo ln -sf /opt/anaconda3/envs/airsim/bin/clang-8 /opt/anaconda3/envs/airsim/bin/clang++-8

# Install AirSim
git clone git@github.com/Microsoft/AirSim.git /opt/AirSim
cd /opt/AirSim
./setup.sh
./build.sh
```




