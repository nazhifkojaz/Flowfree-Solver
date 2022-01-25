using System.Collections.Generic;
using System;
using System.Linq;
public class BtAlgo
{
    private Board _problem;
    public Board Problem
    {
        get { return _problem; }
        set { _problem = value; }
    }
    private List<State> _openList;
    public List<State> OpenList
    {
        get { return _openList; }
        set { _openList = value; }
    }

    private int[] _counter;

    public BtAlgo(Board problem)
    {
        _problem = problem;
        // _counter = Enumerable.Repeat(1, problem.ColorCounter.Length).ToArray();
    }
    // public bool search()
    // {
    //   // best case scenario
    //   if (_problem.IsAssigned()) return true;
    //   else
    //   {
    //     // iterate through the states
    //     foreach (var state in _problem.UnassignedStates())
    //     {
    //       // iterate through its domain and assign it with a value
    //       foreach (var candidate in state.Domain)
    //       {
    //         state.Value = candidate;
    //         _problem.NodesCount++;
    //         // FC.Maintain(_problem);
    //         // check the validity if it's valid then continue
    //         if(_problem.IsValid())
    //         {
    //           if(search()) return true;
    //           // search();
    //         }
    //         // backtrack one step and assign another value
    //         // FC.Restore();
    //         state.Value = -1;
    //       }
    //       // for in recursive? bad idea.
    //       // for (var i = 0; i < state.Domain.Count; i++)
    //       // {
    //       //   state.Value = state.Domain[i];
    //       //   // FC.Maintain(_problem);
    //       //   if(_problem.IsValid())
    //       //   {
    //       //     if(search()) return true;
    //       //   }
    //       //   // FC.Restore();
    //       //   state.Value = -1;
    //       // }
    //     }
    //   }
    //   return false;
    // }


    // in this updated search method, the algorithm search from each preassigned states' head and tail.
    // basically each color (both their heads and tails) are trying to connect to each other
    // this method have (much) smaller B compared to previous method
    public bool search()
    {
        // finished scenario
        if (_problem.IsAssigned()) return true;
        else
        {
            //iterate through active states
            foreach (var current in _problem.GetActiveStatesOrdered())
            // foreach (var current in _problem.GetActiveStates()) //this is without MRV
            {
                current.Active = false;
                //iterate through current state's unassigned peers
                //this part can also be categorized as 'forward checking', right?
                foreach (var peer in current.GetUnassignedPeersOrdered(_problem.GetColorPair(current.Id, current.Value), _problem.Width))
                // foreach (var peer in current.GetUnassignedPeers())
                {
                    peer.Active = true;
                    peer.Value = current.Value;
                    _problem.NodesCount++;

                    if (_problem.IsValid())
                    {
                        if (search()) return true;
                    }

                    peer.Value = -1;
                    peer.Active = false;
                }
                current.Active = true;
            }
        }
        // Console.WriteLine("failed");
        return false;
    }

    public void RestructureBoard()
    {
        foreach (var state in _problem.GetInactiveStatesOrdered())
        {
            if (!state.Active) Crawling(state); //if a solution found, then 
        }
        // if(_problem.isActivated()) return true;
        // else
        // {
        //   foreach (var current in _problem.GetInactiveStatesOrdered())
        //   {
        //       current.Active = true;
        //       _counter[current.Id]++;
        //       if(_counter[current.Id] == 0 || _counter[current.Id] == _problem.ColorCounter[current.Id])
        //         current.Preassigned = true;

        //       foreach (var peer in current.GetInactivePeers())
        //       {
        //           peer.Active = true;

        //       }
        //   }
        // }
        // return false;
    }

    public bool Crawling(State current)
    {
        _problem.NodesCount++;
        if (_problem.isActivated())
        {
            return true;
        }
        else
        {
            _problem.States[current.Id].Active = true;
            if (_counter[current.Value] == 1 || _counter[current.Value] == _problem.ColorCounter[current.Value])
                _problem.States[current.Id].Preassigned = true;
            _counter[current.Value]++;
            foreach (var peer in current.Peers)
            {
                // if the peer has different color, switch with exisiting colors
                List<State> friend = _problem.GetInactiveStatesByColor(current.Value, current.Id);
                State temp = peer;
                if (current.Value != peer.Value && friend.Count > 0)
                {
                    SwitchStates(peer.Id, friend[0].Id);
                    // Console.WriteLine($"id = {current.Id}; peer = {peer.Id}; friend = {friend[0].Id}");
                    // _problem.PrintBoard();
                }
                if (_problem.IsValid())
                    if (Crawling(peer)) return true;

                if (current.Value != peer.Value && friend.Count > 0)
                    SwitchStates(peer.Id, friend[0].Id);
            }
            _problem.States[current.Id].Active = false;
            _counter[current.Value]--;
            if (_counter[current.Value] == 1 || _counter[current.Value] == _problem.ColorCounter[current.Value])
                _problem.States[current.Id].Preassigned = false;
        }
        return false;
    }

    public void SwitchStates(int a, int b)
    {
        State temp = _problem.States[b];
        _problem.States[b] = _problem.States[a];
        _problem.States[a] = temp;
        
        _problem.ConnectStates();
    }
}