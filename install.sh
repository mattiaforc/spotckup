pip3 uninstall spotckup -y
shopt -s nullglob
if [ $# -eq 0 ]; then
  wheels=(dist/*.whl)
  if [ ${#wheels[@]} -gt 1 ]; then
    echo "Found ${#wheels[@]} wheels in the dist folder: "
    for i in "${!wheels[@]}"; do
      printf "\t%s\n" "$((i + 1))) ${wheels[i]}"
    done
    echo "Which one do you want to install?"
    read -r num
    pip3 install "${wheels[num - 1]}"
  else
    pip3 install "${wheels[0]}"
  fi
elif [ $# -eq 1 ]; then
  pip3 install "$1"
else
  echo "Usage: $0 <path to wheel>"
fi
