#pragma once
#include <iostream>
#include <iomanip>
#include <conio.h>
#include <time.h>
#include <Windows.h>
#include <stdlib.h>

#define KEY_UP 72
#define KEY_DOWN 80
#define KEY_LEFT 75
#define KEY_RIGHT 77

#define COLOR_BACK 16
#define FORE_RED 4
#define FORE_GREEN 10
#define FORE_BLUE 1
#define FORE_CREAM 14
#define FORE_GOLD 6

using namespace std;

class SlidingPuzzle
{
private:
	int height;
	int width;
	int** theBoard;
	int fillCounter;															//Increments during initialization to fill the array.
	bool winFlag;																//Returns "True" if the current board matches the guide array.
	int swapTile;																//Temporary storage when swapping tiles.
	int si1;																	//"Slide Index 1". Shortened to fit as an array index.
	int si2;																	//"Slide Index 2".
	int tempArray[120][120];													//Until I can figure out how to NOT do this, for comparing to the current board.
	int crazyMoves;																//A random number holder for when the scramble obliterates the board.
	bool wait = true;															//Stops destructor from triggering when a custom board leaves scope.
	HANDLE currentConsole;

public:
	SlidingPuzzle()
	{
		height = 3;
		width = 3;
		theBoard = NULL;
		theBoard = new(int*[height]);
		fillCounter = 1;
		currentConsole = GetStdHandle(STD_OUTPUT_HANDLE);
		srand(time(NULL));
	}
	SlidingPuzzle(int myHeight, int myWidth)
	{
		height = myHeight;
		width = myWidth;
		theBoard = NULL;
		theBoard = new(int*[height]);
		fillCounter = 1;
		currentConsole = GetStdHandle(STD_OUTPUT_HANDLE);
		srand(time(NULL));
	}
	void initializeBoard()														//Becomes unstable if you input too fast. Gives errors or assigns incorrect numbers. Larger boards increase likelihood.
	{
		si1 = height - 1;
		si2 = width - 1;

		for (int c = 0; c < height; c++)
		{
			theBoard[c] = new(int[width]);
		}
		for (int a = 0; a < height; a++)
		{
			for (int b = 0; b < width; b++)
			{
				theBoard[a][b] = fillCounter;
				fillCounter++;
			}
		}
	}
	void slideTile(int direction)
	{
		switch (direction)
		{
		case KEY_UP:
			if (si1 > 0)
			{
				swapTile = theBoard[si1][si2];									//If statements protect against sliding off the board.
				theBoard[si1][si2] = theBoard[si1 - 1][si2];
				theBoard[si1 - 1][si2] = swapTile;
				si1--;
			}
			break;
		case KEY_DOWN:
			if (si1 < height - 1)
			{
				swapTile = theBoard[si1][si2];
				theBoard[si1][si2] = theBoard[si1 + 1][si2];
				theBoard[si1 + 1][si2] = swapTile;
				si1++;
			}
			break;
		case KEY_LEFT:
			if (theBoard[si1][si2 - 1] > 0)
			{
				swapTile = theBoard[si1][si2];
				theBoard[si1][si2] = theBoard[si1][si2 - 1];
				theBoard[si1][si2 - 1] = swapTile;
				si2--;
			}
			break;
		case KEY_RIGHT:
			if (theBoard[si1][si2 + 1] > 0)
			{
				swapTile = theBoard[si1][si2];
				theBoard[si1][si2] = theBoard[si1][si2 + 1];
				theBoard[si1][si2 + 1] = swapTile;
				si2++;
			}
			break;
		default:
			break;
		}
	}
	void scrambleBoard()
	{
		for (int d = 0; d < 10000; d++)
		{
			crazyMoves = rand() % 4 + 1;
			switch (crazyMoves)
			{
			case 1:
				crazyMoves = KEY_UP;
				break;
			case 2:
				crazyMoves = KEY_DOWN;
				break;
			case 3:
				crazyMoves = KEY_LEFT;
				break;
			case 4:
				crazyMoves = KEY_RIGHT;
				break;
			default:
				break;
			}
			slideTile(crazyMoves);
		}
	}
	void printBoard()
	{
		system("CLS");
		cout << endl;
		for (int e = 0; e < height; e++)
		{
			SetConsoleTextAttribute(currentConsole, FORE_CREAM);
			cout << "   |";
			for (int f = 0; f < width; f++)
			{
				if (theBoard[e][f] != (height * width)) 
				{
					if (theBoard[e][f] == tempArray[e][f])
					{
						SetConsoleTextAttribute(currentConsole, FORE_GREEN);
					}
					else
					{
						SetConsoleTextAttribute(currentConsole, FORE_RED);
					}
					cout << setw(3) << theBoard[e][f];							//Unstable if input is too fast and/or too large. Triggers a breakpoint.
					SetConsoleTextAttribute(currentConsole, FORE_CREAM);
					cout << "|";
				}
				else
				{
					SetConsoleTextAttribute(currentConsole, FORE_BLUE);
					cout << setw(3) << "* ";
					SetConsoleTextAttribute(currentConsole, FORE_CREAM);
					cout << "|";
				}
			}
			cout << endl;
			if (e < height - 1)
			{
				cout << "   |";
				for (int g = 0; g < width; g++)
				{
					cout << "---|";
				}
			}
			cout << endl;
		}
	}
	bool isBoardSolved()
	{		
		winFlag = false;
		fillCounter = 1;
		for (int h = 0; h < height; h++)
		{
			for (int i = 0; i < width; i++)
			{
				tempArray[h][i] = fillCounter;
				fillCounter++;
			}
		}
		for (int j = 0; j < height; j++)
		{
			for (int k = 0; k < width; k++)
			{
				if (theBoard[j][k] == tempArray[j][k])
				{
					winFlag = true;
				}
				else
				{
					return false;
				}
			}
		}
		return winFlag;
	}
	~SlidingPuzzle()															//Destroys allocated memory and my sanity.
	{
		if (wait == false)
		{
			for (int i = 0; i < width; i++)
			{
				delete[] theBoard[i];
				theBoard[i] = NULL;
			}
			delete[] theBoard;
			theBoard = NULL;
		}
		else
		{
			wait = false;
		}
	}
};

class Timer
{
private:
	double startTime;
	double endTime;
	bool started;
	bool ticking;
	bool stopped;
	int hours;
	int minutes;
	int seconds;
	int milliseconds;
	HANDLE currentConsole = GetStdHandle(STD_OUTPUT_HANDLE);

public:
	Timer();
	bool start();																//Only if the watch was stopped, set started and ticking flags, unset stopped flag. Records start time.
	bool stop();																//Only if the watch was ticking, set stopped flag, unset ticking flag. Records stop time.
	bool isTicking();															//Only if the watch was started, set ticking flag, unset started flag.
	void resetTimer();															//Reinitializes timer to default settings.
	void displayTimer();														//Outputs the elapsed time in 00:00:00.000 format.
};
