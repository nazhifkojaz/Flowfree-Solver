using System.Collections.Generic;
using System;
using System.Linq;

public class PSBoard
{
    private List<PSState> _states;
    public List<PSState> States
    {
        get { return _states; }
        set { _states = value; }
    }
    private int _colors;
    public int Colors
    {
        get { return _colors; }
        set { _colors = value; }
    }
    private int _boardSize;
    public int BoardSize
    {
        get { return _boardSize; }
        set { _boardSize = value; }
    }

    private Random _rand;
    private int _pointer;

    public PSBoard(int boardSize, int n_colors)
    {
        _colors = n_colors;
        _boardSize = boardSize;
        _rand = new Random();

        CreateStates();
        ConnectStates();
        // PrintBoard();
        // if (Populate()) PrintBoard();
        // else Console.WriteLine("Populate failed");
    }

    public void PrintBoard()
    {
        for (var i = 0; i < _boardSize; i++)
        {
            for (var j = 0; j < _boardSize; j++)
            {
                Console.Write(_states[i * _boardSize + j].Value + "\t");
            }
            Console.WriteLine("");
        }
    }

    public void CreateStates()
    {
        _states = new List<PSState>();
        for (int i = 0; i < _boardSize * _boardSize; i++)
            _states.Add(new PSState(i));
    }

    public void ConnectStates()
    {
        int row = 0, col = 0;
        for (int i = 0; i < _boardSize * _boardSize; i++)
        {
            col = i % _boardSize;
            row = i / _boardSize;

            if (col - 1 >= 0) _states[i].Peers.Add(_states[i - 1]); //left
            if (col + 1 < _boardSize) _states[i].Peers.Add(_states[i + 1]); //right
            if (row - 1 >= 0) _states[i].Peers.Add(_states[i - _boardSize]); //upper
            if (row + 1 < _boardSize) _states[i].Peers.Add(_states[i + _boardSize]); //bottom
        }
    }

    public List<PSState> GetUnassignedStates()
    {
        List<PSState> temp = new List<PSState>();
        foreach (var state in _states)
            if (state.Value == -1) temp.Add(state);
        return temp;
    }

    public int GetEmptyIndex()
    {
        int idx;
        do
        {
            idx = _rand.Next(_boardSize * _boardSize);
        } while (_states[idx].Value != -1);
        return idx;
    }

    public bool Populate()
    {
        int colCount;
        int failCount = 0;
        int pointer = 0;
        while (pointer < _colors)
        {
            colCount = 0;
            if (failCount == 50) return false;
            int idx = GetEmptyIndex();
            // Console.WriteLine(pointer);

            if (GrowColorBlock(idx, pointer))
            {
                foreach (var state in _states)
                {
                    if(state.Value == pointer) colCount++;
                }
                // Console.WriteLine($"{pointer} + {colCount}");
                Console.WriteLine();
                PrintBoard();
                pointer++;
            } 
            else failCount++;
        }
        Console.WriteLine(pointer);
        Console.WriteLine(_colors);

        return true;
    }

    public bool GrowColorBlock(int id, int color, int counter = 0)
    {
        if (counter > 2) return true; //continue to populate
        else //keep growing the color
        {
            List<PSState> randomizedPeers = _states[id].Peers.OrderBy(a => _rand.Next()).ToList();
            foreach (var peer in randomizedPeers)
            {
                if (peer.Value == -1)
                {
                    peer.Value = color;
                    if(GrowColorBlock(peer.Id, color, counter++)) return true;
                }
                peer.Value = -1;
            }
        }
        return false;
    }
}