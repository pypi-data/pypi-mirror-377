#! python3
# -*- coding: utf-8 -*-

"""A Python interface to FirmaSAT <https://cryptosys.net/firmasat/>."""

# firmasat.py

# ************************** LICENSE *****************************************
# Copyright (C) 2016-25 David Ireland, DI Management Services Pty Limited.
# t/a CryptoSys <https://di-mgt.com.au> <https://cryptosys.net>
# This code is provided 'as-is' without any express or implied warranty.
# Free license is hereby granted to use this code as part of an application
# provided this license notice is left intact. You are *not* licensed to
# share any of this code in any form of mass distribution, including, but not
# limited to, reposting on other websites or in any source code repository.
# ****************************************************************************

import platform
from ctypes import create_string_buffer, c_char_p, c_int

__version__ = "10.70.0"
# History:
# [10.70.0] Update for v10.70.
# [10.50.0] Rewrite for Python 3.
#   Updated to match core library version 10.50 (2023-04-18)
# [0.1.1] Minor updates (2016-08-28).
# [0.1.0] First Python interface to FirmaSAT (2016-08-26).


# OUR EXPORTED CLASSES
__all__ = (
    'Sello', 'Tfd',
    'Pkix', 'Xmlu', 'HashAlg',
    'Gen', 'Err',
    'Error',
)

# Our global DLL/so library object for FirmaSAT
if platform.system() == 'Windows':
    from ctypes import windll
    _didll = windll.diFirmaSAT2
else:
    from ctypes import cdll
    _didll = cdll.LoadLibrary('libfirmasat.so')

# Global constants
_INTMAX = 2147483647
_INTMIN = -2147483648


def _isanint(v):
    try: v = int(v)
    except ValueError: pass
    return isinstance(v, int)


class Error(Exception):
    """Raised when a call to a core FirmaSAT library function returns an error,
    or some obviously wrong parameter is detected."""

    # Google Python Style Guide: "The base exception for a module should be called Error."

    def __init__(self, value):
        """."""
        self.value = value

    @staticmethod
    def _isanint(v):
        try:
            v = int(v)
        except ValueError:
            pass
        return isinstance(v, int)

    def __str__(self):
        """Behave differently if value is an integer or not."""
        if (Error._isanint(self.value)):
            n = int(self.value)
            s1 = "ERROR CODE %d: %s" % (n, Err.error_lookup(n))
        else:
            s1 = "ERROR: %s" % (self.value)
        se = Err.last_error()
        return "%s%s" % (s1, ": " + se if se else "")


class Gen:
    """General info about the core FirmaSAT library DLL."""

    @staticmethod
    def version():
        """Return the release version of the core library DLL as an integer value."""
        return _didll.SAT_Version()

    @staticmethod
    def compile_time():
        """Return date and time the core library DLL was last compiled."""
        nchars = _didll.SAT_CompileTime(None, 0)
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.SAT_CompileTime(buf, nchars)
        return buf.value.decode()[:nchars]

    @staticmethod
    def module_name():
        """Return full path name of the current process's core library DLL."""
        nchars = _didll.SAT_ModuleName(None, 0, 0)
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.SAT_ModuleName(buf, nchars, 0)
        return buf.value.decode()[:nchars]

    @staticmethod
    def core_platform():
        """Return the platform of the core library DLL: ``Win32`` or ``X64``."""
        nchars = 5
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.SAT_Platform(buf, nchars)
        return buf.value.decode()[:nchars]

    @staticmethod
    def comments():
        """Get additional information about the core DLL module."""
        nchars = _didll.SAT_Comments(None, 0, 0)
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.SAT_Comments(buf, nchars, 0)
        return buf.value.decode()[:nchars]

    @staticmethod
    def licence_type():
        """Return licence type: "D"=Developer "T"=Trial."""
        n = _didll.SAT_LicenceType()
        return chr(n)


class Err():
    """Details of errors returned by the core library."""

    @staticmethod
    def last_error():
        """Return the last error message set by the toolkit, if any."""
        nchars = _didll.SAT_LastError(None, 0)
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.SAT_LastError(buf, nchars)
        # NB: Last error may contain Latin-1 chars
        try:
            result = buf.value.decode()
        except UnicodeError:
            result = buf.value.decode('ISO-8859-1')
        return result

    @staticmethod
    def error_lookup(n):
        """Return a description of error code ``n``."""
        nchars = _didll.SAT_ErrorLookup(None, 0, c_int(n))
        buf = create_string_buffer(nchars + 1)
        nchars = _didll.SAT_ErrorLookup(buf, nchars, c_int(n))
        return buf.value.decode()[:nchars]

    @staticmethod
    def format_error_message(errcode=0):
        """Return an error message string for the last error.

        Args:
            errcode (int): Error code returned by last call.

        Returns:
            str: Error message as a string.
        """
        s1 = "ERROR"
        if (errcode != 0):
            s1 += " (%d): %s" % (errcode, Err.error_lookup(errcode))
        se = Err.last_error()
        return "%s%s" % (s1, ": " + se if se else "")


class HashAlg:
    """Hash (message digest) algorithms (for legacy use)."""
    DEFAULT = 0  #: Use default digest algorithm
    # MD5 = 0x10  # obsolete
    SHA1 = 0x20  #: Force SHA-1 digest (legacy)


class Sello:
    """Operates on the sello (signature) node in a SAT XML document."""

    class SignOpts:
        """Bitwise options for signing XML."""
        DEFAULT = 0  #: Default options (add BOM, empty elements in form ``<foo></foo>``)
        NOBOM = 0x2000  #: Do not add byte-order mark (BOM) to file [default = add]
        USEEMPTYELEMENTS = 0x20000  #: Output empty elements in form ``<foo />``
        BIGFILE = 0x8000000  #: Speed up processing of large files

    @staticmethod
    def sign_xml(newfile, basefile, keyfile, password, certfile, signopts=0, hashalg=0):
        """Sign an XML file (file <-- file).

        Args:
            newfile (str): Name of new file to be created.
            basefile (str): Name of base XML file to be signed.
            keyfile (str): Name of private key file (or string containing key data in PEM format)
            password (str): Password for key file
            certfile (str): Name of X.509 certificate file to be included in output XML
                (or string containing certificate data in base64 or PEM format).
            signopts (Sello.SignOpts): Options -- see :class:`Sello.SignOpts`
            hashalg (HashAlg): Message digest algorithm to use in signature (optional).

        Returns:
            int: 0 if successful, otherwise a nonzero error code.

        Note:
            Any existing file called ``newfile`` will be overwritten without warning;
            however, the input and output files can be the same.
            The base XML file must have an empty ``Sello`` attribute node to be completed.
            If a certificate file ``certfile`` is specified then the Certificado and NoCertificado
            nodes will be overwritten in the output file with the values in the certificate file.
            If a certificate file is not specified then the ``Certificado`` value in the XML will be used.

            A version 4 CFDi document to be signed must use the ``"cfdi:"`` namespace prefix.
            For CFD v4 the ``NoCertificado`` attribute in the input must be set to the correct certificate
            serial number before signing.
            In a ``Retenciones`` document you must set the ``CertNum`` attribute before signing.
            In a ``ControlesVolumetricos`` document you must set both the ``noCertificado`` and ``certificado``
            attributes before signing.
        """
        noptions = signopts or hashalg
        n = _didll.SAT_SignXml(newfile.encode(), basefile.encode(), keyfile.encode(), password.encode(), certfile.encode(), noptions)
        if n != 0: raise Error(-n if n < 0 else n)
        return n

    @staticmethod
    def verify_sig(xmlfile, certfile=""):
        """Verify the signature (sello) in an XML file.

        Args:
            xmlfile (str): Full path to XML file.
            certfile (str): Optional X.509 certificate file to override ``Certificado`` in XML.

        Returns:
            int: 0 if signature is verified, otherwise a nonzero error code
            -- see :func:`Err.error_lookup`
        """
        n = _didll.SAT_VerifySignature(xmlfile.encode(), certfile.encode(), 0)
        return -n if n < 0 else n

    @staticmethod
    def make_digest(xmlfile, hashalg=HashAlg.DEFAULT):
        """Form the message digest of piped string (cadena) from an XML file.

        Args:
            xmlfile (str): Full path to XML file.
            hashalg (HashAlg): Option hash algorithm.

        Returns (str):
            Message digest in hex format.

        Note:
            This creates the message digest directly from the data in the XML document.
            Use :func:`Sello.extract_digest_from_sig` to extract the digest from the signature.
        """
        nc = _didll.SAT_MakeDigestFromXml(None, 0, xmlfile.encode(), hashalg)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_MakeDigestFromXml(buf, nc, xmlfile.encode(), hashalg)
        return buf.value.decode()

    @staticmethod
    def make_pipestring(xmlfile):
        """Create the "piped" string (cadena original) from an XML file.

        Args:
            xmlfile (str): Full path to XML file.

        Returns (str):
            Piped string in UTF-8 encoding.
        """
        nc = _didll.SAT_MakePipeStringFromXml(None, 0, xmlfile.encode(), 0)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_MakePipeStringFromXml(buf, nc, xmlfile.encode(), 0)
        return buf.value.decode()[:nc]

    @staticmethod
    def make_sig(xmlfile, keyfile, password, hashalg=0):
        """Create the signature (sello) from an XML file and private key.

        Args:
            xmlfile: Full path to XML file
            keyfile: Name of private key file
            password: Password
            hashalg: Message digest algorithm to use in signature (optional).

        Returns:
            Signature in base64 format or empty string on error.
        """
        opts = int(hashalg)
        nc = _didll.SAT_MakeSignatureFromXmlEx(None, 0, xmlfile.encode(), keyfile.encode(), password.encode(), opts)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_MakeSignatureFromXmlEx(buf, nc, xmlfile.encode(), keyfile.encode(), password.encode(), opts)
        return buf.value.decode()

    @staticmethod
    def extract_digest_from_sig(xmlfile, certfile=""):
        """Extract the message digest from the signature (sello) in an XML file.

        This extracts the message digest from the ``sello`` in the XML document.
        Use :func:`Sello.make_digest` to create the digest from the data in the document.

        Returns:
            Message digest in hex format.
        """
        nc = _didll.SAT_ExtractDigestFromSignature(None, 0, xmlfile.encode(), certfile.encode(), 0)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_ExtractDigestFromSignature(buf, nc, xmlfile.encode(), certfile.encode(), 0)
        return buf.value.decode()

    @staticmethod
    def sign_xml_file_to_buf(xmlfile, keyfile, password, certfile, signopts=0, hashalg=0):
        """Sign XML file returning output in a buffer (bytes <-- file).

        Args:
            xmlfile: Name of base XML file to be signed.
            keyfile: Name of private key file (or string containing key data in PEM format).
            password: Password for key file.
            certfile: Name of X.509 certificate file to be included in output XML
                (or string containing certificate data in base64 or PEM format).
            signopts: Options -- see :class:`Sello.SignOpts`.
            hashalg: Message digest algorithm to use in signature (optional).

        Returns:
            Signed XML data in a byte array.

        Note:
            Output bytes are always UTF-8 encoded.
        """
        opts = int(signopts) or int(hashalg)
        nc = _didll.SAT_SignXmlToString(None, 0, xmlfile.encode(), keyfile.encode(), password.encode(), certfile.encode(), opts)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_SignXmlToString(buf, nc, xmlfile.encode(), keyfile.encode(), password.encode(), certfile.encode(), opts)
        return bytes(buf.value)

    @staticmethod
    def sign_xml_data_to_buf(xmldata, keyfile, password, certfile, signopts=0, hashalg=0):
        """Sign XML data returning output in a buffer (buf <-- buf).

        Args:
            xmldata: Byte array containing XML data.
            keyfile: Name of private key file (or string containing key data in PEM format).
            password: Password for key file.
            certfile: Name of X.509 certificate file to be included in output XML
                (or string containing certificate data in base64 or PEM format).
            signopts: Options -- see :class:`Sello.SignOpts`.
            hashalg: Message digest algorithm to use in signature (optional).

        Returns:
            Signed XML data in a byte array.

        Note:
            Output bytes are always UTF-8 encoded.

        """
        opts = int(signopts) or int(hashalg)
        bufin = bytes(xmldata)
        nc = _didll.SAT_SignXmlToString(None, 0, bufin, keyfile.encode(), password.encode(), certfile.encode(), opts)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_SignXmlToString(buf, nc, bufin, keyfile.encode(), password.encode(), certfile.encode(), opts)
        return bytes(buf.value)

    @staticmethod
    def insert_cert(newfile, basefile, certfile):
        """Insert certificate information into an XML document and output to a new file.

        Args:
            newfile (str): Name of new file to be created.
            basefile (str): Name of base XML file to be processed.
            certfile (str): Name of X.509 certificate file to be included in output XML
                (or string containing certificate data in base64 or PEM format).

        Returns:
            int: 0 if successful, otherwise a nonzero error code.

        """
        noptions = 0
        n = _didll.SAT_InsertCert(newfile.encode(), basefile.encode(), certfile.encode(), noptions)
        if n != 0: raise Error(-n if n < 0 else n)
        return n

    @staticmethod
    def insert_cert_to_string(basefile, certfile):
        """Insert certificate information into an XML document and output to memory.

        Args:
            basefile (str): Name of base XML file to be processed.
            certfile (str): Name of X.509 certificate file to be included in output XML
                (or string containing certificate data in base64 or PEM format).

        Returns:
            str: XML data as a string.
        """
        noptions = 0
        nc = _didll.SAT_InsertCertToString(None, 0, basefile.encode(), certfile.encode(), noptions)
        if nc < 0: raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_InsertCertToString(buf, nc, basefile.encode(), certfile.encode(), 0)
        return buf.value.decode()


class Tfd:
    """Operates on the Timbre Fiscal Digital (TFD) element, if present."""

    # Internal constant
    _SAT_TFD = 0x8000

    @staticmethod
    def make_digest(xmlfile, hashalg=HashAlg.DEFAULT):
        """Form the message digest of cadena original del Timbre Fiscal Digital del SAT (TFD piped String) from CFDI document."""
        opts = int(hashalg) or Tfd._SAT_TFD
        nc = _didll.SAT_MakeDigestFromXml(None, 0, xmlfile.encode(), opts)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_MakeDigestFromXml(buf, nc, xmlfile.encode(), opts)
        return buf.value.decode()

    @staticmethod
    def make_pipestring(xmlfile):
        """Create the cadena original del Timbre Fiscal Digital del SAT (TFD piped string) from CFDI document."""
        opts = Tfd._SAT_TFD
        nc = _didll.SAT_MakePipeStringFromXml(None, 0, xmlfile.encode(), opts)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_MakePipeStringFromXml(buf, nc, xmlfile.encode(), opts)
        return buf.value.decode()

    @staticmethod
    def make_sig(xmlfile, keyfile, password, hashalg=0):
        """Create the ``selloSAT`` signature as a base64 String from TFD data in CFDI document.

        Args:
            xmlfile: Full path to XML file
            keyfile: Name of private key file
            password: Password
            hashalg: Message digest algorithm to use in signature (optional).

        Returns:
            Signature in base64 format or empty string on error.

        Note:
            Assumes you are a PAC with a valid SAT signing key.
        """
        opts = int(hashalg) or Tfd._SAT_TFD
        nc = _didll.SAT_MakeSignatureFromXmlEx(None, 0, xmlfile.encode(), keyfile.encode(), password.encode(), opts)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_MakeSignatureFromXmlEx(buf, nc, xmlfile.encode(), keyfile.encode(), password.encode(), opts)
        return buf.value.decode()

    @staticmethod
    def extract_digest_from_sig(xmlfile, certfile):
        """Extracts the message digest from the selloSAT node in Timbre Fiscal Digital of CFDI document.

        Args:
            xmlfile: Full path to XML file
            certfile: X.509 certificate file of PAC who signed the TFD (required)

        Returns:
            Message digest in hex format or empty string on error
        """
        opts = Tfd._SAT_TFD
        nc = _didll.SAT_ExtractDigestFromSignature(None, 0, xmlfile.encode(), certfile.encode(), opts)
        if nc < 0: raise Error(-nc)
        if nc == 0: return ""
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_ExtractDigestFromSignature(buf, nc, xmlfile.encode(), certfile.encode(), opts)
        return buf.value.decode()

    @staticmethod
    def verify_sig(xmlfile, certfile):
        """Verify the selloSAT signature in TFD node of CFDI document.

        Args:
            xmlfile: Full path to XML file
            certfile: X.509 certificate file of PAC who signed the TFD (required)

        Returns:
            int: 0 if match is OK, otherwise a nonzero error code -- see :func:`Err.error_lookup`
        """
        n = _didll.SAT_VerifySignature(xmlfile.encode(), certfile.encode(), Tfd._SAT_TFD)
        return -n if n < 0 else n

    @staticmethod
    def add_signed_tfd(newFile, inputFile, keyFile, password, certFile):
        """Add a signed Timbre Fiscal Digital (TFD) element to a CFDI document.

        Args:
            newFile: Name of new file to be created.
            inputFile: Name of existing CFDI file.
            keyFile: Name of PAC's private key file.
            password: Password for private key.
            certFile: Name of PAC's X.509 certificate that matches the keyFile.

        Returns:
            int: 0 if successful, otherwise a nonzero error code
            -- see :func:`Err.error_lookup`.

        Note:
            The inputFile must be a version 3.2 CFDI document already signed with a
            ``sello`` field and no existing TFD element.
            The TFD will be timestamped using the system clock and a fresh UUID will be generated.
            No other XML processing is carried out except inserting the TFD element.
        """
        n = _didll.SAT_SignXml(newFile.encode(), inputFile.encode(), keyFile.encode(), password.encode(), certFile.encode(), Tfd._SAT_TFD)
        if (n != 0): raise Error(-n if n < 0 else n)
        return n


class Pkix():
    """PKI X.509 security utilities."""

    class Query:
        """Options for certificate query."""
        NOTAFTER = "notAfter"         #: Get certificate expiry date
        NOTBEFORE = "notBefore"       #: Get certificate start date
        ORGNAME = "organizationName"  #: Get organization name of issuer (expecting "Servicio de Administración Tributaria")
        RFC = "rfc"                   #: Get RFC of subject (expecting 12 or 13 characters)
        SERIALNUM = "serialNumber"    #: Get decoded serial number (expecting 20 decimal digits)
        SIGALG = "sigAlg"             #: Get algorithm used to sign certificate (e.g. ``sha256WithRSAEncryption``)
        KEYSIZE = "keySize"           #: Get size in bits of certificate's public key (e.g. "2048")

    class KeyOpt:
        """Options for key output."""
        DEFAULT = 0              #: Default (unencrypted base64 string)
        ENCRYPTED_PEM = 0x10000  #: Key as encrypted private key in PEM format

    class KeyFormat:
        """Format for saved key files."""
        DEFAULT = 0     #: Default = Binary
        BINARY = 0      #: Binary DER-encoded
        PEM = 0x10000   #: PEM textual format

    @staticmethod
    def query_cert(filename, query):
        """Query an X.509 certificate file for selected information.

        Args:
            filename (str): X.509 file or XML file with ``certificado`` node or a base64 cert string
            query (str): A valid query string -- see :class:`Pkix.Query`

        Returns:
            str: Result of query

        Example::

            n = Sello.query_cert('AC4_SAT.cer', 'keySize')  # '4096'
            s = Sello.query_cert('cfdv40-ejemplo.xml', 'serialNumber')  # 30001000000300023708
        """
        opts = 0
        nc = _didll.SAT_QueryCert(None, 0, filename.encode(), query.encode(), opts)
        if nc < 0: raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_QueryCert(buf, nc, filename.encode(), query.encode(), opts)
        return buf.value.decode()

    @staticmethod
    def get_cert_as_string(fileName):
        """Get the certificate data as a base64 string.

        Args:
            fileName (str): X.509 certificate file or XML file with ``certificado`` node.

        Returns:
            str: Certificate data as a string of base64 characters.

        Note:
            Use to obtain the value for the ``Certificado`` node from an X.509 .CER file.
            If input is an XML file, this is equivalent to
            ``Xmlu.get_attribute(fileName, "Certificado", "Comprobante")``
        """
        nc = _didll.SAT_GetCertAsString(None, 0, fileName.encode(), 0)
        if nc < 0: raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_GetCertAsString(buf, nc, fileName.encode(), 0)
        return buf.value.decode()

    @staticmethod
    def get_key_as_string(fileName, password, keyopt=0):
        """Get the private key data as a base64 string suitable for a
        ``llaveCertificado`` element in a ``Cancelacion`` XML document.

        Args:
            fileName (str): Encrypted private key file
            password (str): Password for encrypted private key
            keyopt: Options -- see :class:`Pkix.KeyOpt`

        Returns:
            str: Private key data as a string of base64 characters,
            or an empty string on error.

        Note:
            CAUTION: this reveals your private key in unsecured form. Use with care!
        """
        opts = int(keyopt)
        nc = _didll.SAT_GetKeyAsString(None, 0, fileName.encode(), password.encode(), opts)
        if nc < 0: raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_GetKeyAsString(buf, nc, fileName.encode(), password.encode(), opts)
        return buf.value.decode()

    @staticmethod
    def check_key_and_cert(keyFile, password, certFile):
        """Verify that the public key in an X.509 certificate matches the private key.

        Returns:
            int: 0 if match is OK, otherwise a nonzero error code -- see :func:`Err.error_lookup`
        """
        n = _didll.SAT_CheckKeyAndCert(keyFile.encode(), password.encode(), certFile.encode(), 0)
        # No exception raised - just return the error code
        return -n if n < 0 else n

    @staticmethod
    def write_pfx_file(pfxFile, pfxPassword, keyFile, keyPassword, certFile):
        """Create a PFX (PKCS-12) file in base64 format suitable for a Cancelación.

        Args:
            pfxFile (str): Name of output PFX file to be created
            pfxPassword (str): Password to open new PFX file
            keyFile (str): Name of encrypted key file
            keyPassword (str): Password for encrypted key file
            certFile (str): Name of X.509 certificate file

        Returns:
            int: 0 if successful, otherwise a nonzero error code
            -- see :func:`Err.error_lookup`.
        """
        n = _didll.SAT_WritePfxFile(pfxFile.encode(), pfxPassword.encode(), keyFile.encode(), keyPassword.encode(), certFile.encode(), 0)
        if n != 0: raise Error(-n if n < 0 else n)
        return n

    @staticmethod
    def new_key_file(newFile, newPassword, keyFile, keyPassword, keyformat=0):
        """Save key file with a new password.

        Args:
            newFile (str): Name of output PFX file to be created
            newPassword (str): Password to open new PFX file
            keyFile (str): Name of encrypted key file
            keyPassword (str): Password for encrypted key file
            keyformat (Pkix.KeyFormat): Format to save file -- see :class:`Pkix.KeyFormat`

        Returns:
            int: 0 if successful, otherwise a nonzero error code
            -- see :func:`Err.error_lookup`.
        """
        noptions = keyformat
        n = _didll.SAT_NewKeyFile(newFile.encode(), newPassword.encode(), keyFile.encode(), keyPassword.encode(), "".encode(), noptions)
        if n != 0: raise Error(-n if n < 0 else n)
        return n

    @staticmethod
    def uuid():
        """Generate a Universally Unique IDentifier (UUID) compliant with RFC 4122.

        Returns:
            A 36-character UUID string freshly generated at random.

        Example::

            'ea4ce835-de5d-4082-8475-47f8e531b254'
        """
        nc = _didll.SAT_Uuid(None, 0, 0)
        if nc < 0: raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_Uuid(buf, nc, 0)
        return buf.value.decode()


class Xmlu():
    """XML utilities."""

    @staticmethod
    def validate_xml(xmlFile, loose=False):
        """Validate an XML file against SAT specifications.

        Args:
            xmlFile: Full path to XML file to be validated.
            loose: Use loose XML restrictions.

        Returns:
            int: 0 if successful, otherwise a nonzero error code
            -- see :func:`Err.error_lookup`.

        Note:
            This just checks that the XML structure is valid.
            It does *not* verify the signature (use :func:`Sello.verify_sig`).
            If this finds an error, your XML file definitely needs fixing,
            but some attribute facet errors may not be detected.
        """
        _SAT_XML_LOOSE = 0x4000
        opts = _SAT_XML_LOOSE if loose else 0
        n = _didll.SAT_ValidateXml(xmlFile.encode(), opts)
        return -n if n < 0 else n

    @staticmethod
    def receipt_version(xmlFile):
        """Find version number of Comprobante (receipt) element or ID number for other supported document types.

        Args:
            xmlFile: Name of XML file

        Returns:
            int: a positive integer indicating the type and version of SAT document,
            otherwise a negative error code -- see :func:`Err.error_lookup`.

            - 40 = Comprobante document with Version="4.0"
            - 33 = Comprobante document with version="3.3"
            - 1010/1020 = Retenciones document with Version="1.0"/"2.0"
            - 2011/2013 = CatalogoCuentas document with Version="1.1"/"1.3"
            - 2111/2113 = BalanzaComprobacion document with Version="1.1"/"1.3"
            - 2211/2213 = PolizasPeriodo document with Version="1.1"/"1.3"
            - 2312/2313 = AuxiliarFolios document with Version="1.2"/"1.3"
            - 2411/2413 = AuxiliarCtas document with Version="1.1"/"1.3"
            - 2511 = SelloDigitalContElec document with Version="1.1"
            - 4011 = ControlesVolumetricos document with Version="1.1"
        """
        n = _didll.SAT_XmlReceiptVersion(xmlFile.encode(), 0)
        if (n < 0): raise Error(-n)
        return n

    @staticmethod
    def fix_bom(outputFile, inputFile):
        """Add a UTF-8 byte order mark (BOM) to a file if not already present.

        Args:
            outputFile: Name of output file to be created with BOM.
            inputFile: Name of input file (must be valid UTF-8 encoded).

        Returns:
            int: 0 if successful, otherwise a nonzero error code
            -- see :func:`Err.error_lookup`.
        """
        n = _didll.SAT_FixBOM(outputFile.encode(), inputFile.encode(), 0)
        if (n != 0): raise Error(-n if n < 0 else n)
        return n

    @staticmethod
    def get_attribute(xmlfile, attributename, elementname):
        """Extract attribute data from an XML file.

        Args:
            xmlfile: Full path to XML file.
            attributename: Name of attribute.
            elementname: Name of element which has attribute.

        Returns:
            Attribute data in a string (perhaps empty) or "!NO MATCH!" if match not found.

        Raises:
            firmasat.Error: if file cannot be found.

        Note:
            Setting ``elementName=""`` will output the value of the named attribute from the root element of the
            XML document. Setting both ``elementName=""`` and ``attributeName=""``
            will output the name of the root element itself.
        """
        _NO_MATCH_ERROR = -21
        # _NOMATCHSTR = "!NO MATCH!NO_COINCIDE!"  # "!NO_COINCIDE!"
        nc = _didll.SAT_GetXmlAttribute(None, 0, xmlfile.encode(), attributename.encode(), elementname.encode())
        if (0 == nc): return ""
        if (_NO_MATCH_ERROR == nc): return Xmlu.xml_no_match()
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_GetXmlAttribute(buf, nc, xmlfile.encode(), attributename.encode(), elementname.encode())
        return buf.value.decode()

    @staticmethod
    def xml_no_match():
        """Error message returned when failed to find a match.

        Use to test for existence of a node when using :func:`Xmlu.get_attribute`.

        Returns (str):
            Error message (default = "!NO MATCH!")
        """
        _NOMATCHSTR = "!NO MATCH!NO_COINCIDE!"
        return _NOMATCHSTR

    @staticmethod
    def asciify(xmlfile_orstr):
        """Replace non-ASCII characters in an XML document with XML numeric character references (where permitted).

        Args:
            xmlfile_orstr (str): Full path to XML file or XML data in a string.

        Returns:
            str: XML document as a string with non-ASCII characters replaced by XML numeric character references.

        Raises:
            firmasat.Error: if file cannot be found or is illegal XmL.

        Note:
            In almost all cases, the output contains only US-ASCII characters and can safely
            be used as input to other functions without concern for character encoding issues.

            In certain cases, some characters in an XML document cannot be replaced by a
            numeric character reference, for example where they are used in an element or
            attribute *name*, such as ``Año="2016"``. In these cases, they are left as
            UTF-8-encoded characters.
        """
        nc = _didll.SAT_Asciify(None, 0, xmlfile_orstr.encode(), 0)
        if (0 == nc): return ""
        if (nc < 0): raise Error(-nc)
        buf = create_string_buffer(nc + 1)
        nc = _didll.SAT_Asciify(buf, nc, xmlfile_orstr.encode(), 0)
        return buf.value.decode()[:nc]


class _NotUsed:
    """Dummy for parsing."""
    pass


# PROTOTYPES (derived from diFirmaSat2.h)
# If wrong argument type is passed, these will raise an `ArgumentError` exception
#     ArgumentError: argument 1: <type 'exceptions.TypeError'>: wrong type
_didll.SAT_Version.argtypes = []
_didll.SAT_CompileTime.argtypes = [c_char_p, c_int]
_didll.SAT_ModuleName.argtypes = [c_char_p, c_int, c_int]
_didll.SAT_LicenceType.argtypes = []
_didll.SAT_LastError.argtypes = [c_char_p, c_int]
_didll.SAT_ErrorLookup.argtypes = [c_char_p, c_int, c_int]
_didll.SAT_MakePipeStringFromXml.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.SAT_MakeSignatureFromXml.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p]
_didll.SAT_MakeSignatureFromXmlEx.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_int]
_didll.SAT_ValidateXml.argtypes = [c_char_p, c_int]
_didll.SAT_VerifySignature.argtypes = [c_char_p, c_char_p, c_int]
_didll.SAT_SignXml.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
_didll.SAT_MakeDigestFromXml.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.SAT_ExtractDigestFromSignature.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_int]
_didll.SAT_GetCertNumber.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.SAT_GetCertExpiry.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.SAT_GetCertAsString.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.SAT_GetXmlAttribute.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p]
_didll.SAT_GetXmlAttributeEx.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_int]
_didll.SAT_CheckKeyAndCert.argtypes = [c_char_p, c_char_p, c_char_p, c_int]
_didll.SAT_XmlReceiptVersion.argtypes = [c_char_p, c_int]
_didll.SAT_FixBOM.argtypes = [c_char_p, c_char_p, c_int]
_didll.SAT_GetKeyAsString.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_int]
_didll.SAT_WritePfxFile.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
_didll.SAT_QueryCert.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_int]
_didll.SAT_SignXmlToString.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
_didll.SAT_Uuid.argtypes = [c_char_p, c_int, c_int]
_didll.SAT_Comments.argtypes = [c_char_p, c_int, c_int]
_didll.SAT_Platform.argtypes = [c_char_p, c_int]
_didll.SAT_Asciify.argtypes = [c_char_p, c_int, c_char_p, c_int]
_didll.SAT_InsertCert.argtypes = [c_char_p, c_char_p, c_char_p, c_int]
_didll.SAT_InsertCertToString.argtypes = [c_char_p, c_int, c_char_p, c_char_p, c_int]
_didll.SAT_NewKeyFile.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_char_p, c_int]
