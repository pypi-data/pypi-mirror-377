#! python3
# -*- coding: utf8 -*-

"""Some tests for `firmasat.py` the Python interface to CryptoSys FirmaSAT."""

# test_firmasat.py: version 10.70.0
# $Date: 2025-09-15 12:05:00 $

# ************************** LICENSE *****************************************
# Copyright (C) 2016-25 David Ireland, DI Management Services Pty Limited.
# All rights reserved. <https://di-mgt.com.au> <https://cryptosys.net>
# The code in this module is licensed under the terms of the MIT license.
# For a copy, see <http://opensource.org/licenses/MIT>
# ****************************************************************************

from firmasat import *  # @UnusedWildImport
import os
import sys
import pytest
import shutil
import random
from glob import iglob

_MIN_FSA_VERSION = 107036

# Show some info about the core CryptoSys DLL
print("INFO ABOUT CORE DLL...")
print("FSA version =", Gen.version())
print("module_name =", Gen.module_name())
print("compile_time =", Gen.compile_time())
print("platform =", Gen.core_platform())
print("licence_type =", Gen.licence_type())
print("comments =", Gen.comments())
# Show some system values
print("SOME SYSTEM VALUES...")
print("sys.getdefaultencoding()=", sys.getdefaultencoding())
print("sys.getfilesystemencoding()=", sys.getfilesystemencoding())
print("sys.platform()=", sys.platform)
print("cwd =", os.getcwd())

if Gen.version() < _MIN_FSA_VERSION:
    raise Exception(('Require PKI version ',
                    str(_MIN_FSA_VERSION) + ' or greater'))

# GLOBAL VARS
# Remember CWD where we started
start_dir = os.getcwd()
# Temp directory to use as CWD for tests - set by  `setup_temp_dir()`
ourtmp_dir = ""
# Flag to delete tmp directory when finished - used in `reset_start_dir()`
# Change with command-line argument `nodelete` - see `main()`
delete_tmp_dir = True


# JIGGERY-POKERY FOR A TEMP WORKING DIRECTORY
#    start_dir/
#        test_firmasat.py  # this module
#        work/             # this _must_ exist
#            <all required test files>
#            tmp.XXXXXXXX/    # created by `setup_temp_dir()`
#                <copy of all required test files>
#                <files created by tests>


def setup_temp_dir():
    """Set up a fresh temp directory to work in."""
    global ourtmp_dir
    # `work` should be a sub-directory of the cwd and must exist
    work_dir = os.path.join(start_dir, "work")
    print("\nExpecting to find work dir:", work_dir)
    assert os.path.isdir(work_dir)
    # It should contain all the required test files
    # Create a temp sub-directory in `work` -- random 8 hex digits
    r1 = random.randrange(0, (1 << 16))
    r2 = random.randrange(0, (1 << 16))
    ourtmp_dir = os.path.join(
        work_dir, "tmp." + format(r1, '04X') + format(r2, '04X'))
    os.mkdir(ourtmp_dir)
    assert (os.path.isdir(ourtmp_dir))
    # Copy the required temp files
    for f in iglob(os.path.join(work_dir, "*.*")):
        if (os.path.isfile(f) and not f.endswith('.zip')):
            shutil.copy(f, ourtmp_dir)

    # Set CWD to be inside temp
    os.chdir(ourtmp_dir)
    print("Working in new temp directory:", os.getcwd())


def reset_start_dir():
    """Set CWD back to where we started and delete temp dir."""
    if not os.path.isdir(start_dir):
        return
    if (ourtmp_dir == start_dir):
        return
    os.chdir(start_dir)
    print("")
    # print "CWD:", os.getcwd()
    # Remove the temp direcory
    if (delete_tmp_dir and 'tmp.' in ourtmp_dir):
        print("Removing temp directory:", ourtmp_dir)
        shutil.rmtree(ourtmp_dir, ignore_errors=True)
    else:
        print("Temp directory '%s' is left in place." % (ourtmp_dir))


# MORE JIGGERY_POKERY FOR py.test
# Thanks to Brian Okken for the base code
# <http://pythontesting.net/framework/pytest/pytest-session-scoped-fixtures/>

@pytest.fixture(scope="module", autouse=True)
def divider_module(request):
    print(("\n   --- module %s() start ---" % request.module.__name__))
    setup_temp_dir()

    def fin():
        print(("\n   --- module %s() done ---" % request.module.__name__))
        reset_start_dir()
    request.addfinalizer(fin)


@pytest.fixture(scope="function", autouse=True)
def divider_function(request):
    print(("\n   --- function %s() start ---" % request.function.__name__))
    os.chdir(ourtmp_dir)

    def fin():
        print(("\n   --- function %s() done ---" % request.function.__name__))
        os.chdir(start_dir)
    request.addfinalizer(fin)


# FILE-RELATED UTILITIES
def read_binary_file(fname):
    with open(fname, "rb") as f:
        return bytearray(f.read())


def read_text_file(fname):
    with open(fname, "rb") as f:
        return f.read().decode()


def write_file(fname, data):
    with open(fname, "wb") as f:
        f.write(data)


def _print_file(fname):
    """Print contents of text file"""
    s = read_text_file(fname)
    print(s)


def _dump_file(fname):
    """Print contents of text file with filename header and rulers"""
    s = read_text_file(fname)
    ndash = (24 if len(s) > 24 else len(s))  # hack
    print("FILE:", fname)
    print("-" * ndash)
    print(s)
    print("-" * ndash)


def _file_has_bom(fname):
    """Returns True if file has a UTF-8 BOM or False if not."""
    buf = read_binary_file(fname)
    if (len(buf) < 3):
        return False
    # BOM consists of three bytes (0xEF, 0xBB, 0xBF)
    return (buf[0] == 0xEF and buf[1] == 0xBB and buf[2] == 0xBF)


# ERROR
def disp_error(n):
    """Display details of last error."""
    s = Err.last_error()
    print("ERROR %d: %s: %s" % (n, Err.error_lookup(n), "\n" + s if s else ""))


###################
# THE TESTS PROPER
###################

def test_version():
    print("VERSION:", Gen.version())
    assert Gen.version() >= _MIN_FSA_VERSION


def test_error_lookup():
    print("\nLOOKUP SOME ERROR CODES...")
    for n in range(10):
        s = Err.error_lookup(n)
        print("error_lookup(" + str(n) + ")=" + s)
        assert (len(s) > 0)


def test_make_digest():
    print("\nFORM MESSAGE DIGESTS...")
    fname = 'cfdv40-ejemplo.xml'
    print("FILE:", fname)
    dig = Sello.make_digest(fname)
    print("DEFAULT:", dig)
    dig = Sello.make_digest(fname, HashAlg.SHA1)
    print("SHA-1  :", dig)

    dig = Sello.make_digest('cfdv40-ejemplo.xml')
    print("dig    :", dig)


def test_make_pipestring_and_sig():
    print("\nCREATE PIPE STRING...")
    fname = 'cfdv40-ejemplo.xml'
    print("FILE:", fname)
    s = Sello.make_pipestring(fname)
    print(s)
    keyfile = 'emisor.key'
    passwd = '12345678a'
    sig = Sello.make_sig(fname, keyfile, passwd)
    print("SIG:", sig)


def test_query_cert():
    print("\nQUERY X.509 CERT...")
    fname = 'cfdv40-ejemplo-signed-tfd.xml'
    print("FILE:", fname)
    query = 'serialNumber'
    s = Pkix.query_cert(fname, query)
    print("Pkix.query_cert(" + query + ")=[" + s + "]")
    query = 'keySize'
    s = Pkix.query_cert(fname, query)
    print("Pkix.query_cert(" + query + ")=[" + s + "]")
    query = 'organizationName'
    s = Pkix.query_cert(fname, query)
    print("Pkix.query_cert(" + query + ")=[" + s + "]")

    fname = "AC4_SAT.cer"
    print("FILE:", fname)
    query = 'serialNumber'
    s = Pkix.query_cert(fname, query)
    print("Pkix.query_cert(" + query + ")=[" + s + "]")
    query = 'keySize'
    s = Pkix.query_cert(fname, query)
    print("Pkix.query_cert(" + query + ")=[" + s + "]")

    try:
        _ = Pkix.query_cert(fname, "BADQUERY")
    except Error as e:
        print("(Expected) Error:", e)
    else:
        raise Exception("Test should have failed.")

    n = Pkix.query_cert('AC4_SAT.cer', 'keySize')
    print("keySize =", n)
    n = Pkix.query_cert('AC4_SAT.cer', Pkix.Query.KEYSIZE)
    print("Query.KEYSIZE =", n)


def test_validate_xml():
    print("\nVALIDATE XML SYNTAX...")

    # A valid XML file
    n = Xmlu.validate_xml('cfdv40-ejemplo.xml')
    assert (0 == n)

    fname = 'cfdv40-ejemplo.xml'
    n = Xmlu.validate_xml(fname)
    print("validate_xml('%s') returns %d (expected zero => OK)" % (fname, n))

    print("EXPECTING ERRORS...")
    # XML with a non-conforming attribute
    fname = "cfdv40-iedu-badcurp.xml"
    n = Xmlu.validate_xml(fname)
    print("validate_xml('%s') returns %d (expected nonzero error)" % (fname, n))
    if (n != 0):
        disp_error(n)
    assert (n != 0)
    # print "But..."
    n = Xmlu.validate_xml(fname, loose=True)
    print("validate_xml('%s', loose) returns %d (expected zero => OK)" % (fname, n))
    assert (0 == n)

    # Not an XML file
    fname = "emisor.cer"
    n = Xmlu.validate_xml(fname)
    print("validate_xml('%s') returns %d (expected nonzero error)" % (fname, n))
    if (n != 0):
        disp_error(n)
    assert (n != 0)

    print("...END OF EXPECTED ERRORS.")


def test_get_attribute():
    print("\nGET ATTRIBUTE FROM XML...")

    fname = 'cfdv40-ejemplo.xml'
    s = Xmlu.get_attribute(fname, "Nombre", "cfdi:Emisor")
    print("Xmlu.get_attribute() returns %s" % (s))

    # Get i'th element until no match found
    for i in range(1, 100):
        elem = f"Concepto[{i}]"
        a = Xmlu.get_attribute(fname, "Descripcion", elem)
        print(f"{elem}={a}")
        if (a == Xmlu.xml_no_match()):
            break


def test_receipt_id():
    print("\nGET COMPROBANTE VERSION OR ID NUMBER...")

    n = Xmlu.receipt_version('cfdv40-ejemplo.xml')
    assert (40 == n)

    # Other types of files
    for (fname, exp) in [
        ("cfdv40-ejemplo.xml", 40),
        ("Ejemplo_Retenciones-base.xml", 1010),
        ("AAA010101AAA201501CT-base.xml", 2011),
        ("AAA010101AAA201501BN-base.xml", 2111),
        ("ConVolE12345-signed2015.xml", 4011),
    ]:
        print("FILE:", fname)
        n = Xmlu.receipt_version(fname)
        print("  receipt_version() returns %d (expected %d)" % (n, exp))
        assert (n == exp)
        # Show root element of document
        print("  ROOT=%s" % (Xmlu.get_attribute(fname, "", "")))


def test_uuid():
    print("\nTEST RANDOM UUID...")
    for dummy in range(5):
        s = Pkix.uuid()
        print(s)


def test_key_string():
    print("\nTEST KEY AS STRING...")

    s = Pkix.get_key_as_string('emisor.key', '12345678a')
    assert (len(s) > 0)
    s = Pkix.get_key_as_string(
        'emisor.key', '12345678a', Pkix.KeyOpt.ENCRYPTED_PEM)
    assert (len(s) > 0)

    fname = "emisor.key"
    pwd = '12345678a'   # CAUTION: do not hardcode passwords
    s = Pkix.get_key_as_string(fname, pwd)
    print("Pkix.get_key_as_string('%s'):\n%s" % (fname, s))
    s = Pkix.get_key_as_string(fname, pwd, Pkix.KeyOpt.ENCRYPTED_PEM)
    print("Pkix.get_key_as_string('%s', ENCRYPTED_PEM):\n%s" % (fname, s))


def test_cert_string():
    print("\nTEST CERT AS STRING...")

    s = Pkix.get_cert_as_string('emisor.cer')
    assert (len(s) > 0)
    s = Pkix.get_cert_as_string('cfdv40-ejemplo-signed-tfd.xml')
    assert (len(s) > 0)

    fname = "emisor.cer"
    s = Pkix.get_cert_as_string(fname)
    print("Pkix.get_cert_as_string('%s'):\n%s" % (fname, s))
    fname = 'cfdv40-ejemplo-signed-tfd.xml'
    s = Pkix.get_cert_as_string(fname)
    print("Pkix.get_cert_as_string('%s'):\n%s" % (fname, s))

    # We can query this string directly as though it were an X.509 file
    print("Query the string directly...")
    rfc = Pkix.query_cert(s, Pkix.Query.RFC)
    print("RFC =", rfc)
    assert (len(rfc) > 0)
    alg = Pkix.query_cert(s, Pkix.Query.SIGALG)
    print("alg =", alg)
    assert (len(alg) > 0)


def test_write_pfx():
    print("\nWRITE PFX FILE...")

    keyFile = "emisor.key"
    certFile = "emisor.cer"
    pfxFile = "emisor.pfx"
    n = Pkix.write_pfx_file(pfxFile, "password1",
                            keyFile, '12345678a', certFile)
    assert (0 == n)
    print("Created new file '%s'" % (pfxFile))
    contents = read_text_file(pfxFile)
    print("Contents:\n" + contents)


def test_check_key_cert():
    print("\nCHECK KEY MATCHES CERT...")

    # Key and cert match
    keyFile = "emisor.key"
    certFile = "emisor.cer"
    n = Pkix.check_key_and_cert(keyFile, '12345678a', certFile)
    print("Pkix.check_key_and_cert() returns %d (expecting 0 => OK)" % (n))

    print("EXPECTING ERRORS...")

    # Key and cert DO NOT match
    keyFile = "emisor.key"
    certFile = "pac.cer"
    n = Pkix.check_key_and_cert(keyFile, '12345678a', certFile)
    print("Pkix.check_key_and_cert() returns %d" % (n))
    disp_error(n)

    # password is wrong
    keyFile = "emisor.key"
    certFile = "pac.cer"
    n = Pkix.check_key_and_cert(keyFile, 'wrong password', certFile)
    print("Pkix.check_key_and_cert() returns %d" % (n))
    disp_error(n)

    # Key file is invalid
    keyFile = "cfdv40-ejemplo.xml"
    certFile = "pac.cer"
    n = Pkix.check_key_and_cert(keyFile, '12345678a', certFile)
    print("Pkix.check_key_and_cert() returns %d" % (n))
    disp_error(n)

    print("...END OF EXPECTED ERRORS.")


def test_sign_xml():
    print("\nSIGN XML FILE...")

    basefile = "cfdv40-ejemplo.xml"
    newfile = "cfdv40-ejemplo-new-signed.xml"
    n = Sello.sign_xml(newfile, basefile, "emisor.key",
                       '12345678a', "emisor.cer")
    print("Sello.sign_xml() returns %d (expecting 0 => OK)" % (n))
    print("Created new XML file '%s'" % (newfile))


def test_extract_digest():
    print("\nEXTRACT DIGEST FROM SELLO...")

    fname = "cfdv40-ejemplo-signed-tfd.xml"
    extr_dig = Sello.extract_digest_from_sig(fname)
    print(extr_dig)

    made_dig = Sello.make_digest(fname)
    print(made_dig)


def test_verify_sig():
    print("\nVERIFY SIGNATURE IN XML FILE...")

    n = Sello.verify_sig('cfdv40-ejemplo-signed-tfd.xml')
    print("Sello.verify_sig() returns %s" % (n))

    # Override certificado included in XML with (correct) cert file
    n = Sello.verify_sig('cfdv40-ejemplo-signed-tfd.xml', 'emisor.cer')
    print("Sello.verify_sig() returns %s" % (n))

    print("ERRORS EXPECTED...")

    # Override with wrong certificate file
    n = Sello.verify_sig('cfdv40-ejemplo-signed-tfd.xml', 'pac.cer')
    print("Sello.verify_sig() returns %s" % (n))
    disp_error(n)

    # Sello has been changed
    n = Sello.verify_sig('cfdv40-ejemplo-badsign.xml')
    print("Sello.verify_sig() returns %s" % (n))
    disp_error(n)

    # File does not exist
    n = Sello.verify_sig('missing.xml')
    print("Sello.verify_sig() returns %s" % (n))
    disp_error(n)

    # Not an XML file
    n = Sello.verify_sig('pac.cer')
    print("Sello.verify_sig() returns %s" % (n))
    disp_error(n)

    print("...END OF EXPECTED ERRORS.")


def test_fix_bom():
    print("\nFIX BOM IN XML FILE...")

    infile = "cfdv40-ejemplo.xml"
    outfile = "cfdv40-ejemplo-nobom.xml"
    print("Create a signed XML file with no BOM...")
    n = Sello.sign_xml(outfile, infile, "emisor.key", '12345678a',
                       "emisor.cer", signopts=Sello.SignOpts.NOBOM)
    print("Sello.sign_xml() returns %d (expecting 0 => OK)" % (n))
    print("Created new XML file '%s'" % (outfile))
    has_bom = _file_has_bom(outfile)
    print("File %s a UTF-8 BOM" % ("DOES NOT have" if not has_bom else "HAS"))

    print("Now add a BOM to it...")
    infile = outfile
    outfile = "cfdv40-ejemplo-withbom.xml"
    n = Xmlu.fix_bom(outfile, infile)
    print("Xmlu.fix_bom() returns %d (expecting 0 => OK)" % (n))
    print("Created new XML file '%s'" % (outfile))
    has_bom = _file_has_bom(outfile)
    print("File %s a UTF-8 BOM" % ("DOES NOT have" if not has_bom else "HAS"))


def test_sign_xml_to_buf():
    print("\nSIGN XML FILE TO BUFFER...")

    basefile = "cfdv40-ejemplo.xml"
    print("bytes <-- file")
    xmlsigned = Sello.sign_xml_file_to_buf(
        basefile, "emisor.key", '12345678a', "emisor.cer")
    print("Signed XML:\n" + xmlsigned.decode()[0:60] + '\n ...[snip]... \n' + xmlsigned.decode()[-60:])
    # Write to disk so we can examine later
    write_file("frombuf1.xml", xmlsigned)

    # Read in file to a byte array, then sign to a buffer
    xmlbase = read_binary_file(basefile)
    print("Read in %d bytes from file" % (len(xmlbase)))
    print("bytes <-- bytes")
    xmlsigned = Sello.sign_xml_data_to_buf(
        xmlbase, "emisor.key", '12345678a', "emisor.cer", signopts=Sello.SignOpts.USEEMPTYELEMENTS)
    print("Signed XML:\n" + xmlsigned.decode()[0:60] + '\n ...[snip]... \n' + xmlsigned.decode()[-60:])
    write_file("frombuf2.xml", xmlsigned)

    # We can pass key file and certificate as "PEM" strings.
    # The "BEGIN/END" encapsulation is optional for a certificate,
    # but is required for the encrypted private key.
    # These strings are from `emisor-pem.cer` and `emisor-pem.key`,
    # respectively.
    # CAUTION: no white space between """ and -----
    certdata = """-----BEGIN CERTIFICATE-----
MIIF+TCCA+GgAwIBAgIUMzAwMDEwMDAwMDAzMDAwMjM3MDgwDQYJKoZIhvcNAQELBQAwggFmMSAwHgY
DVQQDDBdBLkMuIDIgZGUgcHJ1ZWJhcyg0MDk2KTEvMC0GA1UECgwmU2VydmljaW8gZGUgQWRtaW5pc3
RyYWNpw7NuIFRyaWJ1dGFyaWExODA2BgNVBAsML0FkbWluaXN0cmFjacOzbiBkZSBTZWd1cmlkYWQgZ
GUgbGEgSW5mb3JtYWNpw7NuMSkwJwYJKoZIhvcNAQkBFhphc2lzbmV0QHBydWViYXMuc2F0LmdvYi5t
eDEmMCQGA1UECQwdQXYuIEhpZGFsZ28gNzcsIENvbC4gR3VlcnJlcm8xDjAMBgNVBBEMBTA2MzAwMQs
wCQYDVQQGEwJNWDEZMBcGA1UECAwQRGlzdHJpdG8gRmVkZXJhbDESMBAGA1UEBwwJQ295b2Fjw6FuMR
UwEwYDVQQtEwxTQVQ5NzA3MDFOTjMxITAfBgkqhkiG9w0BCQIMElJlc3BvbnNhYmxlOiBBQ0RNQTAeF
w0xNzA1MTgwMzU0NTZaFw0yMTA1MTgwMzU0NTZaMIHlMSkwJwYDVQQDEyBBQ0NFTSBTRVJWSUNJT1Mg
RU1QUkVTQVJJQUxFUyBTQzEpMCcGA1UEKRMgQUNDRU0gU0VSVklDSU9TIEVNUFJFU0FSSUFMRVMgU0M
xKTAnBgNVBAoTIEFDQ0VNIFNFUlZJQ0lPUyBFTVBSRVNBUklBTEVTIFNDMSUwIwYDVQQtExxBQUEwMT
AxMDFBQUEgLyBIRUdUNzYxMDAzNFMyMR4wHAYDVQQFExUgLyBIRUdUNzYxMDAzTURGUk5OMDkxGzAZB
gNVBAsUEkNTRDAxX0FBQTAxMDEwMUFBQTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAJdU
csHIEIgwivvAantGnYVIO3+7yTdD1tkKopbL+tKSjRFo1ErPdGJxP3gxT5O+ACIDQXN+HS9uMWDYnaU
RalSIF9COFCdh/OH2Pn+UmkN4culr2DanKztVIO8idXM6c9aHn5hOo7hDxXMC3uOuGV3FS4ObkxTV+9
NsvOAV2lMe27SHrSB0DhuLurUbZwXm+/r4dtz3b2uLgBc+Diy95PG+MIu7oNKM89aBNGcjTJw+9k+Wz
JiPd3ZpQgIedYBD+8QWxlYCgxhnta3k9ylgXKYXCYk0k0qauvBJ1jSRVf5BjjIUbOstaQp59nkgHh45
c9gnwJRV618NW0fMeDzuKR0CAwEAAaMdMBswDAYDVR0TAQH/BAIwADALBgNVHQ8EBAMCBsAwDQYJKoZ
IhvcNAQELBQADggIBABKj0DCNL1lh44y+OcWFrT2icnKF7WySOVihx0oR+HPrWKBMXxo9KtrodnB1tg
Ix8f+Xjqyphhbw+juDSeDrb99PhC4+E6JeXOkdQcJt50Kyodl9URpCVWNWjUb3F/ypa8oTcff/eMftQ
ZT7MQ1Lqht+xm3QhVoxTIASce0jjsnBTGD2JQ4uT3oCem8bmoMXV/fk9aJ3v0+ZIL42MpY4POGUa/iT
aawklKRAL1Xj9IdIR06RK68RS6xrGk6jwbDTEKxJpmZ3SPLtlsmPUTO1kraTPIo9FCmU/zZkWGpd8ZE
AAFw+ZfI+bdXBfvdDwaM2iMGTQZTTEgU5KKTIvkAnHo9O45SqSJwqV9NLfPAxCo5eRR2OGibd9jhHe8
1zUsp5GdE1mZiSqJU82H3cu6BiE+D3YbZeZnjrNSxBgKTIf8w+KNYPM4aWnuUMl0mLgtOxTUXi9MKnU
ccq3GZLA7bx7Zn211yPRqEjSAqybUMVIOho6aqzkfc3WLZ6LnGU+hyHuZUfPwbnClb7oFFz1PlvGOpN
DsUb0qP42QCGBiTUseGugAzqOP6EYpVPC73gFourmdBQgfayaEvi3xjNanFkPlW1XEYNrYJB4yNjphF
rvWwTY86vL2o8gZN0Utmc5fnoBTfM9r2zVKmEi6FUeJ1iaDaVNv47te9iS1ai4V4vBY8r
-----END CERTIFICATE----"""

    keydata = """-----BEGIN ENCRYPTED PRIVATE KEY-----
MIIFDjBABgkqhkiG9w0BBQ0wMzAbBgkqhkiG9w0BBQwwDgQI5qDMtGWYa2wCAggA
MBQGCCqGSIb3DQMHBAhFAqj+c0f8JASCBMhNUpNUp57vMu8L3LHBKRBTFl0VE3oq
BIEKBHFYYz063iiS0Y3tPW3cplLTSqG25MdbIQcHCxwmPVYNdetHUjqjeR+TklWg
tnMbLqvdMmmRxAFuHXznHFIa4U+YNedhFm7sdR2DsGFijm3vIpUbvpILtpTrhog/
EHAvZXV6+F86cYc9+LUg3d0DRwJc+sWmk+2xOoXvOvvpnnQqfhQxkSknfITmc+HA
WgHbKLK2q6e2RixjpWn0sA9LslYD0ZDn5uhrce+QEfK97asraFfiteqXf2Ll8B54
Ku/er+O2JEu62vVDFumwMtZOuHKH4NbjOmMzKIwRTKp/1jp6OTGYSKIRiTDXnTET
JwgItHahf7UAoM/qnkJa17Ood4hiCYopMyCXdhyMDJoFhWRanQODaiocb7XpMm1S
EpTtHZeKgEVWSc/obYgSgs4iY497UR2MUVZQSCBdRXCgs5g1c31cCwAZ6r41KMoL
OBVLtRXoT0mc0D6ovlwYuJhqYvuwjdNkWJS7qwXuy8b2ux4t027NGUXmgtb9XQDm
8yJrdTtm0CktWPKe7i2tQtBC2tAjduGAlBrzY+whySRN8KUJQbYKhOBaLXgEPI93
wi/SKHJO13WvfqqjKqrqJwB3tvhjz5E1uDKmDFoivdS76uq+k/xpmF5OWBmypWNV
iw7kgvmH1OeTBKYkUHIL85skL6pdycGnTk3g0AmG9xtPYu6pdSqUv+N8QmTdmmdu
85fDEN0fk2t2BRPANsbIqxopVfj5qIwm+8TbZDdNj8OssxrC5sRy5yDBjV4J+x25
3yaILn7wgUR6Yj6GaHUUF4GISmFZ/PTbnVPDd424w6hGV8NKtUHXq5ms2kJXo6XG
iGqjbdePM53QhdSrxTM5Dt76RcAInky6w5s/7gvT/w7tdbVA/SPhp4xgaT8Crmjb
k3upcSqNI0HuROBxOs0gRRAWXScUZJ0Vd1V0F+C5cG2R1CtGTYeRmIAwLwcWf6Dj
Y1Q+TOe/W3eTatOo+gIozjYDCk5ZNfeQzq4p1ApN6+gzS8kNxtvKOYJogjV74RK/
Xl7u7oLv4SZT7Nl1YRpScW1ouIcNNTP0AC+j2OFZ3YueN8CcmvXbgSW8pYRooTxn
Ffo9sdOL624uwRyb2DwwLO0Vo3aBIEIf8sm9sqocXmwh9sxFPEbTXPCuMSao8Qjy
BOlsCem2589NVZs0h0ipGwdbatcjkgf+hzRoYBdlvHtKHJ8gL/A/Ap8z0+TK5NaV
WUA+zXOZRZ66NYfs18DEbJKjwOcnnsLcfAMYoSn697148sL4JBv8IOmM6QXfxCl/
0yU0d5/876L5jOL56lfH0eBk8s2nioAl3yRBl2wlihWi39sA0bsdHFKYEX+LqPBB
CAdxZAvXCCJcdEdxOXSgEiFAmW9+IXFT/WJeGcZ4OmCd3Qf0fxGqFXA/9hIUumWd
e6s0wN8LjXuFZQaMDaaVIGXKguP3OijsfBF0PYzI+L6CfUi2BLaYNJTlbQxbncmW
2PKeDiypgt3ZY1PKV66o5OAJEAkV3vf9cRwXE5T8GwZHA+wx2rWC98hkH15xfI9q
EsYulVdcXWzCF58HFQjUoDon0e/QMukS0eNgq9ipmoKAWKyy7+TQw7Xx3MmqkGlL
HGM=
-----END ENCRYPTED PRIVATE KEY-----;
"""
    # Note that all parameters are passed as strings here: no files involved
    xmlsigned = Sello.sign_xml_data_to_buf(
        xmlbase, keydata, '12345678a', certdata)
    print("Signed XML:\n" + xmlsigned.decode()[0:60] + '\n ...[snip]... \n' + xmlsigned.decode()[-60:])
    print("type(xmlsigned)=", type(xmlsigned))
    write_file("frombuf3.xml", xmlsigned)


def test_tfd():
    print("\nOPERATIONS ON THE TIMBRE FISCAL DIGITAL (TFD)...")
    print("\nCREATE CADENA ORIGINAL DEL TIMBRE FISCAL DIGITAL (PIPESTRING FOR TFD):")
    fname = "cfdv40-ejemplo-signed-tfd.xml"
    s = Tfd.make_pipestring(fname)
    print(s)
    # Form the digest from the element nodes in the XML doc
    s = Tfd.make_digest(fname)
    print(s)
    # Extract the digest from the signature value using the PAC's cert
    certfile = "pac.cer"
    s1 = Tfd.extract_digest_from_sig(fname, certfile)
    print(s1)
    # Should be the same, but ignore case when comparing
    assert (s1.lower() == s.lower())

    print("\nPRETEND WE ARE A PAC WITH A KEY ALLOWED TO SIGN THE TFD:")
    # Create a TFD signature string we could paste into the `SelloSAT` node
    fname = "cfdv40-ejemplo-signed-tfd.xml"
    certfile = "pac.cer"
    keyfile = "pac.key"
    password = "12345678a"
    s = Tfd.make_sig(fname, keyfile, password)
    print(s)
    # Compare with actual `SelloSAT` in doc
    s1 = Xmlu.get_attribute(fname, "SelloSAT", "TimbreFiscalDigital")
    print(s1)
    assert s == s1

    print("\nVERIFY SIGNATURE IN TFD SELLOSAT:")
    n = Tfd.verify_sig(fname, certfile)
    print("Tfd.verifySignature() returns %d (expected 0)" % (n))
    assert 0 == n

    print("\nADD A TFD ELEMENT TO A SIGNED CFDI DOCUMENT USING PAC KEY:")
    # Base file is signed but has no TFD element
    fname = "cfdv40-ejemplo_signed.xml"
    newname = "cfdv40-ejemplo_signed-new-tfd.xml"
    # We have the PAC's private key and cert to do the signing
    certfile = "pac.cer"
    keyfile = "pac.key"
    password = "12345678a"
    n = Tfd.add_signed_tfd(newname, fname, keyfile, password, certfile)
    print("Tfd.add_signed_tfd('%s'-->'%s') returns %d" % (fname, newname, n))
    assert 0 == n
    # Did we make a valid XML file?
    n = Xmlu.validate_xml(newname)
    print("Xmlu.validate_xml() returned %d" % (n))
    assert 0 == n
    # Does it have a valid selloSAT in the TFD?
    n = Tfd.verify_sig(newname, certfile)
    print("Tfd.verify_sig() returned %d" % (n))
    assert 0 == n
    # Show the pipe string. NB different each time
    #  -- timestamped using the system clock and a fresh UUID is generated
    s = Tfd.make_pipestring(newname)
    print(s)


def test_asciify():
    print("\nASCIIFY AN XML DOCUMENT...")
    xmlstr = "<a c='México'/>"
    print(f"OLD=[{xmlstr}]")
    s = Xmlu.asciify(xmlstr)
    print(f"NEW=[{s}]")
    # Now do a file
    fname = "cfdv40-ejemplo.xml"
    print(f"FILE: {fname}")
    s = Xmlu.asciify(fname)
    # Check it's still valid XML
    assert (Xmlu.validate_xml(s) == 0)
    # Check it's digest value is unchanged
    print("SHA-256(original) =" + Sello.make_digest(fname))
    print("SHA-256(asciified)=" + Sello.make_digest(s))
    assert (Sello.make_digest(fname) == Sello.make_digest(s))


def test_insertcert():
    print("\nINSERT CERTIFICATE AND NUMBER INTO CFDI...")
    fname = "cfdv40-ejemplo-nocertnum.xml"
    certfile = "emisor.cer"
    print(f"FILE: {fname}")
    print("Expecting error...")
    n = Xmlu.validate_xml(fname)
    print(f"Xmlu.validate_xml returns {n}:\n {Err.format_error_message(n)}")
    certnum = Xmlu.get_attribute(fname, "NoCertificado", "Comprobante")
    print(f"NoCertificado={certnum}")
    # Now insert Certificado and NoCertificado
    newfile = "cfdv40-ejemplo-with-added-cert.xml"
    n = Sello.insert_cert(newfile, fname, certfile)
    print(f"Sello.insert_cert returns {n}")
    certnum = Xmlu.get_attribute(newfile, "NoCertificado", "Comprobante")
    print(f"NoCertificado(FILE)={certnum}")

    # Repeat but output to a new string, not a file
    xmlstr = Sello.insert_cert_to_string(fname, certfile)
    certnum = Xmlu.get_attribute(xmlstr, "NoCertificado", "Comprobante")
    print(f"NoCertificado(STR)={certnum}")

    # Check against serial number in actual certificate
    serialnum = Pkix.query_cert(certfile, 'serialNumber')
    print(f"serialNumber={serialnum}")
    assert serialnum == certnum


def test_newkeyfile():
    print("\nSAVE KEYFILE WITH A NEW PASSWORD...")
    keyfile = "emisor.key"
    certfile = "emisor.cer"
    oldpassword = "12345678a"
    print(f"Keyfile={keyfile}")
    n = Pkix.check_key_and_cert(keyfile, oldpassword, certfile)
    assert (0 == n)

    newkeyfile = "newkeyfile.key"
    newpassword = "password123"
    n = Pkix.new_key_file(newkeyfile, newpassword, keyfile, oldpassword)
    print(f"Pkix.new_key_file returns {n}")
    print(f"NewKeyfile={newkeyfile}")
    # Check this new key file still works
    n = Pkix.check_key_and_cert(newkeyfile, newpassword, certfile)
    assert (0 == n)

    # Again but saving in PEM format
    newkeyfile = "newkeyfile.pem"
    newpassword = "password123456"
    n = Pkix.new_key_file(newkeyfile, newpassword, keyfile, oldpassword, Pkix.KeyFormat.PEM)
    print(f"Pkix.new_key_file(PEM) returns {n}")
    print(f"NewKeyfile={newkeyfile}")
    # Check this new key file still works
    n = Pkix.check_key_and_cert(newkeyfile, newpassword, certfile)
    assert (0 == n)
    # Read in what should be a text file
    s = read_text_file(newkeyfile)
    print(s[:60] + "\n...\n" + s[-37:])


def main():
    do_all = True  # CHANGE TO SUIT
    for arg in sys.argv:
        global delete_tmp_dir
        if (arg == 'nodelete'):
            delete_tmp_dir = False
        elif (arg == 'some'):
            do_all = False
    setup_temp_dir()

    # DO THE TESTS - EITHER SOME OR ALL
    if (do_all):
        print("DOING ALL TESTS...\n")
        test_version()
        test_error_lookup()
        test_make_digest()
        test_make_pipestring_and_sig()
        test_query_cert()
        test_uuid()
        test_validate_xml()
        test_receipt_id()
        test_cert_string()
        test_key_string()
        test_write_pfx()
        test_check_key_cert()
        test_sign_xml()
        test_fix_bom()
        test_sign_xml_to_buf()
        test_get_attribute()
        test_verify_sig()
        test_extract_digest()
        test_tfd()
        test_asciify()
        test_insertcert()
        test_newkeyfile()

    else:   # just do some tests: comment out as necessary
        print("ONLY DOING SOME TESTS...\n")
        test_version()
#         test_error_lookup()
#         test_make_digest()
#         test_make_pipestring_and_sig()
#         test_query_cert()
#         test_uuid()
#         test_validate_xml()
#         test_receipt_id()
#         test_cert_string()
#         test_key_string()
#         test_write_pfx()
#         test_check_key_cert()
#         test_sign_xml()
#         test_fix_bom()
#         test_sign_xml_to_buf()
#         test_get_attribute()
#         test_verify_sig()
#         test_extract_digest()
#         test_tfd()
#         test_asciify()
#         test_insertcert()
        test_newkeyfile()

    reset_start_dir()
    print("ALL DONE.")


if __name__ == "__main__":
    main()
