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
            row = i % _boardSize;
            
            if(col - 1 >= 0) _states[i].Peers.Add(_states[i-1]); //left
            if(col + 1 < _boardSize) _states[i].Peers.Add(_states[i+1]); //right
            if(row-1 >= 0) _states[i].Peers.Add(_states[i-_boardSize]); //upper
            if(row+1 < _boardSize) _states[i].Peers.Add(_states[i+_boardSize]); //bottom
        }
    }
    
    public List<PSState> GetUnassignedStates()
    {
        List<PSState> temp = new List<PSState>();
        foreach (var state in _states)
            if(state.Value == -1) temp.Add(state);
        return temp;
    }
    
    private int _colorCounter;
    public bool Populate()
    {
        if(_pointer == _colors) return true;
        else
        {
            List<PSState> unassignedStates = GetUnassignedStates().OrderBy(a => _rand.Next()).ToList();
            foreach (var state in unassignedStates)
            {
                
            }
        }
        
        return false;
    }
    
    // public bool PutColorBlock(int color, int id, int counter = 0)
    // {
    //     if(counter == 3) return true;
    //     var randomizedPeers = _states[id].Peers.OrderBy(a => _rand.Next()).ToList();
    //     foreach (var peer in randomizedPeers)
    //     {
    //         if(peer.Value == -1)
    //         {
                
    //         }
    //     }
    //     return false;
    // }
    
    public List<int> GrowColor(int color, int id)
    {
        List<PSState> copy = _states;
        List<int> ids = new List<int>();
        ids.Add(id);
        int activeId = id;
        int counter = 1;
        while (counter < 3)
        {
            List<PSState> randomizedPeer = copy[activeId].Peers.OrderBy(a => _rand.Next()).ToList();
            foreach (var peer in randomizedPeer)
            {
                if(copy[peer.Id].Value == -1)
                {
                    counter += 1;
                    activeId = peer.Id;
                    ids.Add(peer.Id);
                    break;
                }
                return ids;
            }
        }
        return ids;
    }
}