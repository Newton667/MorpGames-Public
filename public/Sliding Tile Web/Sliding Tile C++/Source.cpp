/*Jesse Harvey-Simon - Group Project*/

#include <iostream>
#include <conio.h>
#include <Windows.h>
#include <stdlib.h>
#include "Header.h"

using namespace std;

#define KEY_Q 113

#define FORE_GRAY 8
#define FORE_WHITE 15

int main()
{
	int height = 3;
	int width = 3;
	char custom;
	int direction = 0;
	int moves = 0;
	bool quitGame = false;
	SlidingPuzzle puzzle;
	Timer gameClock;
	HANDLE currentConsole = GetStdHandle(STD_OUTPUT_HANDLE);
	
	cout << endl << "   Sliding Tile Puzzle Game!" << endl;
	cout << "   Set a custom board size? (Y/N)" << endl << "   ";
	cin >> custom;
	while (((custom != 'Y') && (custom != 'y') && (custom != 'N') && (custom != 'n')) || cin.fail())
	{
		cout << "   Ah ah ah. That wasn't a choice." << endl;
		cin >> custom;
	}
	cout << endl;
	if ((custom == 'Y') || (custom == 'y'))
	{
		do
		{
			cout << "   Try not to be unreasonable." << endl;
			cout << "   New Board's Height: ";
			cin >> height;
			cout << "   New Board's Width: ";
			cin >> width;
			cout << endl;
		} while ((height < 3) || (width < 3));
		SlidingPuzzle customPuzzle(height, width);
		puzzle = customPuzzle;
	}
	cout << "   This is where the fun begins." << endl;
	cout << "   Use the Arrow Keys to slide your * tile. Press Q at any time to quit the game." << endl;
	gameClock.resetTimer();																				//Clears any possible initial values.
	puzzle.initializeBoard();																			//Fills the board with numbers.
	puzzle.scrambleBoard();																				//Enters random slide moves.
	puzzle.printBoard();																				//Prints the board.
	gameClock.start();																					//Starts the game clock.
	while (quitGame == false)
	{

		direction = _getch();																			//A first read. Two are necessary for the arrow inputs to work.
		if (direction == KEY_Q)																			//If you press Q, you quit the game.
		{
			SetConsoleTextAttribute(currentConsole, FORE_GRAY);
			cout << endl << "   I wouldn't blame you. Computers have lost too." << endl;				//I used a website to test solutions. It never solved more than a 3x3.
			quitGame = true;
		}
		else
		{
			direction = _getch();																		//Second read. The actual value of an arrow press.
			puzzle.slideTile(direction);																//Slides the tile.
			puzzle.printBoard();
			moves++;
			quitGame = puzzle.isBoardSolved();															//If you win, the game ends.
			if (quitGame == true)
			{
				SetConsoleTextAttribute(currentConsole, FORE_GOLD);
				cout << "   Good job! You beat a " << height << "x" << width << " puzzle!" << endl;
			}
		}
	}
	gameClock.stop();
	gameClock.displayTimer();
	cout << "   Moves Played: " << moves << endl;
	SetConsoleTextAttribute(currentConsole, FORE_WHITE);
	cout << "   Press any key to close." << endl;

	_getch();

	return 0;

}
