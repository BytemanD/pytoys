
echo -e "\033[44;37m      bloack      \033[0m"
black src
echo

echo -e "\033[44;37m    autoflake     \033[0m"
autoflake -ri --remove-all-unused-imports  src
echo

echo -e "\033[44;37m      isort       \033[0m"
isort src
echo

echo -e "\033[44;37m      pylint      \033[0m"
# default max line length is 100
pylint src || exit 1
echo
