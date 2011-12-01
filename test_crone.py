import crone
import datetime
import unittest

class TestFunctions(unittest.TestCase):

    def test_range_parser_minute(self):
        parse = crone.build_parsers()[0]

        self.assertEqual([0], parse("0"))
        self.assertEqual([59], parse("59"))
        self.assertEqual([1,2,3], parse("1,2,3"))
        self.assertEqual([1,2,3], parse("3,2,1"))
        self.assertEqual([1,2,3], parse("1-3"))
        self.assertEqual(range(0, 60, 2), parse("*/2"))
        self.assertEqual(range(0, 60, 5), parse("*/5"))
        self.assertEqual(range(0, 60), parse("*"))
        self.assertEqual([0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50], 
            parse("1,2,3,2-5,*/10"))

        self.assertRaises(Exception, parse, "-1")
        self.assertRaises(Exception, parse, "60")
        self.assertRaises(Exception, parse, "*/")

    def test_range_parser_hour(self):
        parse = crone.build_parsers()[1]

        self.assertEqual([0], parse("0"))
        self.assertEqual([23], parse("23"))
        self.assertEqual([1,2,3], parse("1,2,3"))
        self.assertEqual([1,2,3], parse("3,2,1"))
        self.assertEqual([1,2,3], parse("1-3"))
        self.assertEqual(range(0, 24, 2), parse("*/2"))
        self.assertEqual(range(0, 24, 5), parse("*/5"))
        self.assertEqual(range(0, 24), parse("*"))
        self.assertEqual([0, 1, 2, 3, 4, 5, 10, 20], 
            parse("1,2,3,2-5,*/10"))

        self.assertRaises(Exception, parse, "-1")
        self.assertRaises(Exception, parse, "24")
        self.assertRaises(Exception, parse, "*/")

    def test_range_parser_date(self):
        parse = crone.build_parsers()[2]

        self.assertEqual([1], parse("1"))
        self.assertEqual([31], parse("31"))
        self.assertEqual([1,2,3], parse("1,2,3"))
        self.assertEqual([1,2,3], parse("3,2,1"))
        self.assertEqual([1,2,3], parse("1-3"))
        self.assertEqual(range(1, 32, 2), parse("*/2"))
        self.assertEqual(range(1, 32, 5), parse("*/5"))
        self.assertEqual(range(1, 32), parse("*"))
        self.assertEqual([1, 2, 3, 4, 5, 11, 21, 31], 
            parse("1,2,3,2-5,*/10"))

        self.assertRaises(Exception, parse, "0")
        self.assertRaises(Exception, parse, "32")
        self.assertRaises(Exception, parse, "*/")

    def test_range_parser_month(self):
        parse = crone.build_parsers()[3]

        self.assertEqual([1], parse("1"))
        self.assertEqual([12], parse("12"))
        self.assertEqual([1,2,3], parse("1,2,3"))
        self.assertEqual([1,2,3], parse("3,2,1"))
        self.assertEqual([1,2,3], parse("1-3"))
        self.assertEqual(range(1, 13, 2), parse("*/2"))
        self.assertEqual(range(1, 13, 5), parse("*/5"))
        self.assertEqual(range(1, 13), parse("*"))
        self.assertEqual([1, 2, 3, 4, 5, 11], 
            parse("1,2,3,2-5,*/10"))

        self.assertRaises(Exception, parse, "0")
        self.assertRaises(Exception, parse, "13")
        self.assertRaises(Exception, parse, "*/")

    def test_range_parser_day(self):
        parse = crone.build_parsers()[4]

        self.assertEqual([0], parse("0"))
        self.assertEqual([6], parse("6"))
        self.assertEqual([1,2,3], parse("1,2,3"))
        self.assertEqual([1,2,3], parse("3,2,1"))
        self.assertEqual([1,2,3], parse("1-3"))
        self.assertEqual(range(0, 7, 2), parse("*/2"))
        self.assertEqual(range(0, 7, 5), parse("*/5"))
        self.assertEqual(range(0, 7), parse("*"))
        self.assertEqual([0, 1, 2, 3, 4, 5], 
            parse("1,2,3,2-5,*/10"))

        self.assertRaises(Exception, parse, "-1")
        self.assertRaises(Exception, parse, "7")
        self.assertRaises(Exception, parse, "*/")

    def test_datetime_parser_begin(self):
        parse = crone.build_parsers()[5]

        self.assertEqual(datetime.datetime(2011, 11, 12, 1, 2, 3), 
            parse("2011-11-12T01:02:03"))
        self.assertEqual(datetime.datetime(2000, 1, 1, 0, 0, 0), parse("*"))

        self.assertRaises(Exception, parse, "XXX")

    def test_datetime_parser_end(self):
        parse = crone.build_parsers()[6]

        self.assertEqual(datetime.datetime(2011, 11, 12, 1, 2, 3), 
            parse("2011-11-12T01:02:03"))
        self.assertEqual(datetime.datetime(2099, 12, 31, 23, 59, 59), parse("*"))

        self.assertRaises(Exception, parse, "XXX")

    def test_interval_parser(self):
        parse = crone.build_parsers()[7]

        self.assertEqual(("d", 7), parse("7d"))
        self.assertEqual(("h", 7), parse("7h"))
        self.assertEqual(("m", 7), parse("7m"))
        self.assertEqual(("d", 1), parse("*"))

        self.assertRaises(Exception, parse, "7s")
        self.assertRaises(Exception, parse, "XXX")

    def test_timezone_parser(self):
        parse = crone.build_parsers()[8]

        self.assertEqual("GMT+7", parse("GMT+7"))
        self.assertEqual("A-B.C", parse("A-B.C"))
        self.assertEqual("Australia/Melbourne", parse("Australia/Melbourne"))
        self.assertEqual("UTC", parse("*"))

unittest.main()
