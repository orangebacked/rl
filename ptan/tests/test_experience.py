from unittest import TestCase

import gym
from ptan import experience


class TestExperienceSource(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = gym.make("MountainCar-v0")

    @staticmethod
    def agent_zero(_):
        return 0

    def test_one_step(self):
        exp_source = experience.ExperienceSource(self.env, self.agent_zero, steps_count=1)
        for exp in exp_source:
            self.assertEqual(2, len(exp))
            self.assertIsInstance(exp, tuple)
            self.assertIsInstance(exp[0], experience.Experience)
            self.assertAlmostEqual(exp[0].reward, -1.0)
            self.assertFalse(exp[0].done)
            break

    def test_two_steps(self):
        exp_source = experience.ExperienceSource(self.env, self.agent_zero, steps_count=2)
        for exp in exp_source:
            self.assertEqual(3, len(exp))
            break

    def test_short_game(self):
        env = gym.make('CartPole-v0')
        exp_source = experience.ExperienceSource(env, self.agent_zero, steps_count=1)
        for step, exp in enumerate(exp_source):
            self.assertIsInstance(exp, tuple)
            self.assertIsInstance(exp[0], experience.Experience)
            if exp[0].done:
                self.assertEqual(2, len(exp))
                self.assertIsNotNone(exp[1].state)
                self.assertIsNone(exp[1].reward)
                self.assertIsNone(exp[1].action)
                break
            elif exp[1].done:
                self.assertEqual(2, len(exp))


class TestExperienceReplayBuffer(TestCase):
    @classmethod
    def setUpClass(cls):
        env = gym.make("MountainCar-v0")
        cls.source = experience.ExperienceSource(env, lambda _: 0)

    def test_len(self):
        buf = experience.ExperienceReplayBuffer(self.source, buffer_size=2)
        self.assertEqual(0, len(buf))
        self.assertEqual([], list(buf))

        buf.populate(1)
        self.assertEqual(1, len(buf))

        buf.populate(2)
        self.assertEqual(2, len(buf))

    def test_sample(self):
        buf = experience.ExperienceReplayBuffer(self.source)
        buf.populate(10)
        b = buf.sample(4)
        self.assertEqual(4, len(b))

        buf_ids = list(map(id, buf))
        check = list(map(lambda v: id(v) in buf_ids, b))
        self.assertTrue(all(check))

        b = buf.sample(20)
        self.assertEqual(10, len(b))

    def test_batches(self):
        buf = experience.ExperienceReplayBuffer(self.source)
        buf.populate(10)

        b = list(buf.batches(batch_size=2))
        self.assertEqual(5, len(b))
        self.assertEqual(2, len(b[0]))

        buf.populate(1)
        b = list(buf.batches(batch_size=2))
        self.assertEqual(5, len(b))

        buf.populate(1)
        b = list(buf.batches(batch_size=2))
        self.assertEqual(6, len(b))

        pass