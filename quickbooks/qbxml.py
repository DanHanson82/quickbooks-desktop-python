'Functions for formatting and parsing QBXML'
from collections import OrderedDict

from lxml import etree as xml


def format_request(requestType, request_dictionary=None, qbxmlVersion='13.0', onError='stopOnError'):
    'Format request as QBXML'
    if not request_dictionary:
        request_dictionary = dict()

    section = xml.Element(requestType)
    for key, value in request_dictionary.iteritems():
        section.extend(format_request_part(key, value))
    body = xml.Element('QBXMLMsgsRq', onError=onError)
    body.append(section)
    document = xml.Element('QBXML')
    document.append(body)
    elements = [
        xml.ProcessingInstruction('xml', 'version="1.0"'),
        xml.ProcessingInstruction('qbxml', 'version="%s"' % qbxmlVersion),
        document,
    ]
    return ''.join(xml.tostring(x, encoding='utf-8', pretty_print=True) for x in elements)


def format_request_part(key, value):
    'Format request part recursively'
    # If value is a dictionary,
    if isinstance(value, tuple):
        value = OrderedDict(value)
    if hasattr(value, 'iteritems'):
        part = xml.Element(key)
        for x, y in value.iteritems():
            part.extend(format_request_part(x, y))
        return [part]
    # If value is a list of dictionaries,
    elif hasattr(value, '__iter__'):
        parts = []
        for valueByKey in value:
            if isinstance(valueByKey, tuple):
                valueByKey = OrderedDict(valueByKey)
            part = xml.Element(key)
            for x, y in valueByKey.iteritems():
                part.extend(format_request_part(x, y))
            parts.append(part)
        return parts
    # If value is neither a dictionary nor a list,
    else:
        part = xml.Element(key)
        part.text = str(value)
        return [part]


def parse_response(response):
    'Parse QBXML response into a list of dictionaries'
    document = xml.XML(response)
    body = document[0]
    section = body[0]
    valueByKeys = []
    for part in section:
        valueByKeys.append(parse_response_part(part))
    if not valueByKeys:
        raise Exception(section.get('statusMessage'))
    return valueByKeys


def parse_response_part(part):
    'Parse response part recursively'
    if not part.getchildren():
        return part.text
    valueByKey = {}
    for element in part:
        key = element.tag
        content = parse_response_part(element)
        if key in valueByKey:
            oldValue = valueByKey[key]
            newValue = oldValue if hasattr(oldValue, 'append') else [oldValue]
            newValue.append(content)
        else:
            newValue = content
        valueByKey[key] = newValue
    return valueByKey
