"""
Test colorizers.
"""
from builtins import str

from unittest import TestCase

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from chromalog.colorizer import (
    ColorizedObject,
    Colorizer,
    ColorizableMixin,
)
from chromalog.mark import Mark

from .common import repeat_for_values


class ColorizerTests(TestCase):
    def test_colorizer_get_color_pair_not_found(self):
        colorizer = Colorizer({})
        self.assertEqual(('', ''), colorizer.get_color_pair(['a']))

    def test_colorizer_get_color_pair_found(self):
        colorizer = Colorizer({
            'a': ('[', ']'),
        })
        self.assertEqual(('[', ']'), colorizer.get_color_pair(['a']))

    def test_colorizer_get_color_pair_found_double(self):
        colorizer = Colorizer({
            'a': ('[', ']'),
            'b': ('<', '>'),
        })
        self.assertEqual(('[<', '>]'), colorizer.get_color_pair(['a', 'b']))

    def test_colorizer_get_color_pair_not_found_with_default(self):
        colorizer = Colorizer(
            {
                'a': ('[', ']'),
                'b': ('<', '>'),
            },
            default_color_tag='b',
        )
        self.assertEqual(('<', '>'), colorizer.get_color_pair(['c']))

    def test_colorizer_get_color_pair_found_with_context(self):
        colorizer = Colorizer(
            {
                'a': ('[', ']'),
                'b': ('<', '>'),
            },
        )
        self.assertEqual(('><[', ']><'), colorizer.get_color_pair(['a'], 'b'))

    @repeat_for_values()
    def test_colorizer_converts_unknown_types(self, _, value):
        colorizer = Colorizer(color_map={
            'a': ('[', ']'),
            'b': ('<', '>'),
        })
        self.assertEqual(ColorizedObject(value), colorizer.colorize(value))

    @repeat_for_values()
    def test_colorizer_changes_colorizable_types(self, _, value):
        colorizer = Colorizer(color_map={
            'a': ('[', ']'),
        })
        self.assertEqual(
            ColorizedObject(Mark(value, 'a'), ('[', ']')),
            colorizer.colorize(Mark(value, 'a')),
        )

    @repeat_for_values()
    def test_colorizer_changes_colorizable_types_with_tags(self, _, value):
        colorizer = Colorizer(color_map={
            'a': ('[', ']'),
            'b': ('<', '>'),
        })
        self.assertEqual(
            ColorizedObject(Mark(value, ['a', 'b']), ('[<', '>]')),
            colorizer.colorize(Mark(value, ['a', 'b'])),
        )

    @repeat_for_values()
    def test_colorizer_changes_colorizable_types_with_context(self, _, value):
        colorizer = Colorizer(color_map={
            'a': ('[', ']'),
            'b': ('<', '>'),
        })
        self.assertEqual(
            ColorizedObject(Mark(value, 'a'), ('><[', ']><')),
            colorizer.colorize(Mark(value, 'a'), 'b'),
        )

    @repeat_for_values()
    def test_colorizer_changes_colorizable_types_with_tags_and_context(
        self,
        _,
        value,
    ):
        colorizer = Colorizer(color_map={
            'a': ('[', ']'),
            'b': ('(', ')'),
            'c': ('<', '>'),
        })
        self.assertEqual(
            ColorizedObject(Mark(value, ['a', 'b']), ('><[(', ')]><')),
            colorizer.colorize(Mark(value, ['a', 'b']), 'c'),
        )

    @repeat_for_values({
        "default_colorizable": ColorizableMixin(),
        "specific_colorizable": ColorizableMixin(color_tag='info'),
    })
    def test_colorizable_mixin_has_a_color_tag_attribute_for(self, _, value):
        self.assertTrue(hasattr(value, 'color_tag'))

    def test_colorizer_colorizes_with_known_color_tag(self):
        colorizer = Colorizer(
            color_map={
                'my_tag': ('START_MARK', 'STOP_MARK'),
            },
        )
        result = colorizer.colorize(Mark('hello', color_tag='my_tag'))
        self.assertEqual(
            ColorizedObject(
                Mark(
                    'hello',
                    'my_tag',
                ),
                (
                    'START_MARK',
                    'STOP_MARK',
                ),
            ),
            result,
        )

    def test_colorizer_colorizes_with_known_color_tag_and_default(self):
        colorizer = Colorizer(
            color_map={
                'my_tag': ('START_MARK', 'STOP_MARK'),
                'default': ('START_DEFAULT_MARK', 'STOP_DEFAULT_MARK')
            },
            default_color_tag='default',
        )
        result = colorizer.colorize(Mark('hello', color_tag='my_tag'))
        self.assertEqual(
            ColorizedObject(
                Mark(
                    'hello',
                    'my_tag',
                ),
                (
                    'START_MARK',
                    'STOP_MARK',
                ),
            ),
            result,
        )

    def test_colorizer_doesnt_colorize_with_unknown_color_tag(self):
        colorizer = Colorizer(
            color_map={
                'my_tag': ('START_MARK', 'STOP_MARK'),
            },
        )
        result = colorizer.colorize(Mark('hello', color_tag='my_unknown_tag'))
        self.assertEqual(
            ColorizedObject(Mark('hello', 'my_unknown_tag'), ('', '')),
            result,
        )

    def test_colorizer_colorizes_with_unknown_color_tag_and_default(self):
        colorizer = Colorizer(
            color_map={
                'my_tag': ('START_MARK', 'STOP_MARK'),
                'default': ('START_DEFAULT_MARK', 'STOP_DEFAULT_MARK')
            },
            default_color_tag='default',
        )
        result = colorizer.colorize(Mark('hello', color_tag='my_unknown_tag'))
        self.assertEqual(
            ColorizedObject(
                Mark(
                    'hello',
                    'my_unknown_tag',
                ),
                (
                    'START_DEFAULT_MARK',
                    'STOP_DEFAULT_MARK',
                ),
            ),
            result,
        )

    def test_printer(self):
        colorizer = Colorizer(color_map={
            'a': ('[', ']'),
            'b': ('(', ')'),
            'c': ('<', '>'),
        })
        stream = StringIO()
        printer = colorizer.printer(stream)

        printer(
            'this {} a {value} !',
            'is',
            value=Mark('value', ['a', 'b', 'c']),
        )
        self.assertEqual('this is a [(<value>)] !\n', stream.getvalue())

    def test_printer_with_context(self):
        colorizer = Colorizer(color_map={
            'a': ('[', ']'),
            'b': ('(', ')'),
            'c': ('<', '>'),
        })
        stream = StringIO()
        printer = colorizer.printer(stream)

        printer.with_context('c')(
            'this {} a {value} !',
            'is',
            value=Mark('value', ['a', 'b']),
        )
        self.assertEqual('<this is a ><[(value)]>< !>\n', stream.getvalue())
