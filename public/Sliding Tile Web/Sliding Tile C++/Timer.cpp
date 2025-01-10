#include "Header.h"

Timer::Timer()
{
	startTime = 0;
	endTime = 0;
	started = false;
	ticking = false;
	stopped = true;
	hours = 0;
	minutes = 0;
	seconds = 0;
	milliseconds = 0;
}

bool Timer::start()							//Track when the clock starts.
{
	if (stopped == true)
	{
		started = true;
		stopped = false;
		ticking = true;
		startTime = clock();
	}
	else
	{
		started = false;
		stopped = true;
	}
	return started;
}

bool Timer::stop()							//Track when the clock stops.
{
	if (ticking == true)
	{
		ticking = false;
		stopped = true;
		endTime = clock();
	}
	else
	{
		stopped = false;
	}
	return stopped;
}

bool Timer::isTicking()						//Tracks when the clock is ticking.
{
	if (started == true)
	{
		started = false;
		ticking = true;
	}
	else
	{
		ticking = false;
	}
	return ticking;
}

void Timer::resetTimer()					//Reset the clock after each use.
{
	startTime = 0;
	endTime = 0;
	started = false;
	ticking = false;
	stopped = true;
	hours = 0;
	minutes = 0;
	seconds = 0;
	milliseconds = 0;
}

void Timer::displayTimer()					//Display time in 00:00:00.000 format.
{
	milliseconds = endTime - startTime;
	while (milliseconds >= 1000)
	{
		milliseconds = milliseconds - 1000;
		seconds++;
	}
	while (seconds >= 60)
	{
		seconds = seconds - 60;
		minutes++;
	}
	while (minutes >= 60)
	{
		minutes = minutes - 60;
		hours++;
	}
	cout << "   Time Elapsed: ";
	cout << setfill('0') << setw(2) << hours << ":" << setfill('0') << setw(2) << minutes << ":" << setfill('0') << setw(2) << seconds << "." << setfill('0') << setw(3) << milliseconds << endl;
}
