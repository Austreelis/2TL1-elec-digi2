echo "Automatic flashing script"
echo "Boards:"
boards
echo "---"
echo "Flashing default board at /pyboard"
echo "---"
cp -r src/* /pyboard
echo "---"
echo "Done"
echo "---"
repl ~ machine.soft_reset() ~
