import unittest
from fedcharge.learning import new_table, average, update, greedy, scenario_seed, train
from fedcharge.environment import Station

class LearningTests(unittest.TestCase):
    def test_weighted_aggregation(self):
        a,b=new_table(),new_table()
        a[5][2],b[5][2]=2,6
        result=average([a,b],[1,3])
        self.assertEqual(result[5][2],5)
        result[5][2]=99
        self.assertEqual(a[5][2],2)
        with self.assertRaises(ValueError):
            average([a,b],[0,1])

    def test_terminal_does_not_bootstrap(self):
        q=new_table()
        q[1][0]=100
        update(q,0,2,4,1,True,0.5,0.9)
        self.assertEqual(q[0][2],2)
        update(q,2,2,4,1,False,0.5,0.9)
        self.assertEqual(q[2][2],47)

    def test_independent_rows_and_edf_tie_break(self):
        q=new_table()
        self.assertEqual(greedy(q,0),1)
        q[0][0]=4
        self.assertEqual(q[1][0],0)
        self.assertEqual(greedy(q,0),0)

    def test_seed_namespaces(self):
        train_keys={scenario_seed(1,"train",i,e) for i in range(3) for e in range(100)}
        eval_keys={scenario_seed(1,"evaluation",i,e) for i in range(3) for e in range(100)}
        self.assertFalse(train_keys & eval_keys)
        self.assertEqual(len(train_keys),300)

    def test_training_is_deterministic_and_learns(self):
        stations=[Station("a",4,9,0.4),Station("b",5,17,0.2)]
        config=dict(rounds=2,local_episodes=1,alpha=0.1,gamma=0.9,epsilon_start=0.7,epsilon_end=0.1,epsilon_decay=0.9)
        first=train(stations,config,7)
        self.assertEqual(first,train(stations,config,7))
        self.assertTrue(any(value != 0 for row in first[0] for value in row))
        self.assertNotEqual(first[1][0],first[1][1])

if __name__ == "__main__":
    unittest.main()
