# -*- coding: utf-8 -*-
import sys
import logging


logger = logging.getLogger(__name__)
sublogger = logging.getLogger(__name__+'.baz')

u = (lambda x: x.decode('utf-8')) if sys.version_info < (3,) else (lambda x: x)


def test_fixture_help(testdir):
    result = testdir.runpytest('--fixtures')
    result.stdout.fnmatch_lines(['*caplog*'])


def test_change_level(caplog, monkeypatch):
    caplog.set_level(logging.INFO)
    logger.debug('handler DEBUG level')
    logger.info('handler INFO level')

    assert sublogger.level == logging.NOTSET
    caplog.set_level(logging.CRITICAL, logger=sublogger.name)
    sublogger.warning('logger WARNING level')
    sublogger.critical('logger CRITICAL level')

    assert 'DEBUG' not in caplog.text
    assert 'INFO' in caplog.text
    assert 'WARNING' not in caplog.text
    assert 'CRITICAL' in caplog.text
    assert sublogger.level == logging.CRITICAL
    monkeypatch.undo()
    assert sublogger.level == logging.NOTSET


def test_with_statement(caplog):
    with caplog.at_level(logging.INFO):
        logger.debug('handler DEBUG level')
        logger.info('handler INFO level')

        with caplog.at_level(logging.CRITICAL, logger=sublogger.name):
            sublogger.warning('logger WARNING level')
            sublogger.critical('logger CRITICAL level')

    assert 'DEBUG' not in caplog.text
    assert 'INFO' in caplog.text
    assert 'WARNING' not in caplog.text
    assert 'CRITICAL' in caplog.text


def test_log_access(caplog):
    logger.info('boo %s', 'arg')
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].msg == 'boo %s'
    assert 'boo arg' in caplog.text


def test_record_tuples(caplog):
    logger.info('boo %s', 'arg')

    assert caplog.record_tuples == [
        (__name__, logging.INFO, 'boo arg'),
    ]


def test_unicode(caplog):
    logger.info(u('bū'))
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].msg == u('bū')
    assert u('bū') in caplog.text


def test_clear(caplog):
    logger.info(u('bū'))
    assert len(caplog.records)
    caplog.clear()
    assert not len(caplog.records)


def test_special_warning_with_del_records_warning(testdir):
    p1 = testdir.makepyfile("""
        def test_del_records_inline(caplog):
            del caplog.records()[:]
    """)
    result = testdir.runpytest_subprocess(p1)
    result.stdout.fnmatch_lines([
        "WL1 test_*.py:1 'caplog.records()' syntax is deprecated,"
        " use 'caplog.records' property (or caplog.clear()) instead",
        "*1 pytest-warnings*",
    ])


def test_warning_with_setLevel(testdir):
    p1 = testdir.makepyfile("""
        def test_inline(caplog):
            caplog.setLevel(0)
    """)
    result = testdir.runpytest_subprocess(p1)
    result.stdout.fnmatch_lines([
        "WL1 test_*.py:1 'caplog.setLevel()' is deprecated,"
        " use 'caplog.set_level()' instead",
        "*1 pytest-warnings*",
    ])
