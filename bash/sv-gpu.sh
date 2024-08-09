#!/usr/bin/env bash
# SV
# 
echo "Check if nouveau is loaded"
lsmod | grep nouveau | while read line
do
  if [[ $line == nouveau* ]]; then
    echo "  nouveau is loaded"
    echo "  $line"
    echo "  remove it here"
    echo "  black list it here"
    echo "  initrams here"
    echo "  reboot here"
    break
  else
    echo "  nouveau is not loaded"
    echo "  $line"
  fi 
done
echo ""

echo "Checking if iommu is set"
dmesg | grep -i iommu | while read line
do
  if [[ $line == *"iommu"* ]]; then
    echo "  iommu seems set"
    echo "  $line"
  fi 
done
echo ""

echo "Checking dkms is installed"
dpkg -l | grep dkms | while read line
do
  if [[ $line == *"Dynamic Kernel Module Support"* ]]; then
    echo "  dkms installed"
    echo "  $line"
    # exit here
  elif [[ $line == *"no packages found matching dkms"* ]]; then
    echo "  install dkms here"
  else
    echo "  installed or not?"
    echo "  $line"
  fi
done
echo "'

echo "Install nvidia drivers"
echo "wget http://build.melbourne.nectar.org.au/vgpu/grid/Host_Drivers/nvidia-vgpu-ubuntu-<VERSION>.deb"
echo "dpkg -i nvidia-vgpu-ubuntu-<VERSION>_amd64.deb"
echo ""

echo "hold nvidia driver here"
echo "apt-mark hold nvidia-vgpu-ubuntu-<VERSION>"
echo ""
echo ""
cat /var/lib/dpkg/status | grep -A 1 -i -e nvidia-vgpu-ubuntu- | while read line
do
  echo "  $line"
done

read -p "Enter the Maximum vGPUs per GPU in Equal-Size Mode:" num_vms_per_card
echo "Max vGPU per card $num_vms_per_card"
echo ""

echo "getting number of processors..."
my_cpus=$(lscpu | grep ^CPU\(s\)\: | cut -d':' -f2 | xargs)
echo "Number of processors $my_cpus"
echo ""

my_gpu_cards=$(nvidia-smi --list-gpus | wc -l)
echo "Number of gpu cards $my_gpu_cards"

my_num_vms=$((num_vms_per_card * my_gpu_cards))
echo "Number of VMs (Max vGPU per card * Num of Cards) $my_num_vms"
echo ""
my_cpu_per_vm=$((my_cpus/my_num_vms))
echo "Number of cpu per vm (Num of CPUs / Num of VMs) $my_cpu_per_vm"
echo ""

my_mem=$(free -m | grep ^Mem\: | tr -s ' ' | cut -d' ' -f2)
echo "Memory Total $my_mem"
echo "...taking away 32768..."
my_mem_available=$((my_mem - 32768)) 
echo "Memory available for all VMs $my_mem_available"
mem_per_vm=$((my_mem_available/my_num_vms))
echo "Memory per VM $mem_per_vm"
echo ""
mem_per_vm_g=$((mem_per_vm/1024))
echo "in Gb $mem_per_vm_g"
echo "Flavor ${my_cpu_per_vm}c${mem_per_vm_g}g"

echo ""
first_busid=$(nvidia-smi -q -i 0 | grep 'Bus Id' | tr -s ' ' | cut -d' ' -f5)
echo "First Bus Id $first_busid"
busid_major=${first_busid:4:10}
echo "Bus ID Major ID $busid_major"

busid_major=${busid_major,,}
busid_major=${busid_major//\:/\\:}

dir_busid_major=""
ls -l /sys/class/mdev_bus/ | grep $busid_major | while read line
do
  dir_busid_major=$(echo $line | cut -d' ' -f9)
#  echo "dir_busid_major $dir_busid_major"
  dir_busid_major=${dir_busid_major//\:/\\:}
  echo "dir_busid_major $dir_busid_major"
  echo ""
  echo "Your supported mdev types:"
  dir_mdevs_supported="/sys/class/mdev_bus/${dir_busid_major}/mdev_supported_types/*/name"
  grep NVIDIA $dir_mdevs_supported | grep Q
  break
done
echo ""

