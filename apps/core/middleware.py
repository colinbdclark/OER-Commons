#
#  Copyright 2009, Ryan Kelly.
#  Redistributable under the BSD license, just like Django itself.
#

from StringIO import StringIO
import time
import re

from django.conf import settings
from django.utils.datastructures import MergeDict
from django.http.multipartparser import MultiPartParser


class FakeFileUploadMiddleware:
    """Middlware to fake the upload of some files by the client.

    This middleware can be used to simulate a file upload by the client.
    You might use this, for example, to work around JavaScript security
    restrictions on file uploads when performing in-browser testing.

    The details of the fake files available for upload must be specified
    in the Django setting FAKEUPLOAD_FILE_SPEC, which is a mapping from
    string ids to dictionaries of file properties.  The supported properties
    are as follows:

        * filename:     the name of the file, for display purposes
        * contents:     the contents of the file as a string
        * file:         the server-side file to use for contents
        * chunk_size:   maximum chunk size at which to read from the file
        * sleep_time:   time to sleep between successive reads of the file

    The properties allow you to simulate a variety of upload conditions,
    such as large files and slow uploads.  For example, the following setting
    would make "test1" a fake file containing with contents "I am a testing
    file" that will take 8 seconds to read:

        FAKEUPLOAD_FILE_SPEC = {
          "test1": { "filename"     : "test1.txt",
                     "contents"     : "I am a testing file",
                     "chunk_size"   : 5,    # four chunks in total
                     "sleep_time"   : 2  }  # eight seconds slept in total
        }


    All incoming POST requests are searched for fields with names like
    fakefile_<name>, which correspond to a fake upload of a file in the
    field <name>.  The field value must contain a fake file id as described
    above.  Any such fields are interpreted and sent throuh the standard
    file upload machinery of Django, including triggering of upload handlers.
    The modified request is (in theory) indistinguishable from one in which
    a genuine file upload was performed.

    All outgoing responses are searched for file upload fields.  Each file
    field <name> will be augmented with a hidden input field fakefile_<name>
    which can be used to fake an upload of that file.  For example, this
    simple upload form:

        <form method='POST' enctype='multipart/form-data'>
          <input type='file' name='myfile' />
          <input type='submit' name='upload' value='upload' />
        </form>

    would come out of this middleware looking like this:

        <form method='POST' enctype='multipart/form-data'>
          <input type='hidden' name='fakefile_myfile' />
          <input type='file' name='myfile' />
          <input type='submit' name='upload' value='upload' />
        </form>

    Ordinarily users would fill in the 'myfile' field, but test scripts can
    instead fill in the 'fakefile_myfile' field.  After passing through
    FakeFileUploadMiddleware, the two requests should be indistinguishable.

    The following additional settings can be specified:

        * FAKEUPLOAD_FIELD_NAME:        field name prefix; default "fakefile"
        * FAKEUPLOAD_REWRITE_RESPONSE:  whether to rewrite response bodies
        * FAKEUPLOAD_MIME_BOUNDARY:     boundary to use when encoding the files

    """

    def __init__(self):
        self.file_spec = settings.FAKEUPLOAD_FILE_SPEC
        try:
            self.field_name = settings.FAKEUPLOAD_FIELD_NAME + "_"
        except AttributeError:
            self.field_name = "fakefile_"
        try:
            self.rewrite_response = settings.FAKEUPLOAD_REWRITE_RESPOSNE
        except AttributeError:
            self.rewrite_response = True
        if self.rewrite_response:
            # Yeah yeah, "now I have two problems" etc...
            # It's not worth firing up a HTML parser for this.
            self.file_field_re = re.compile(r'<input\W[^>]*\btype=(\'|"|)file(\'|"|)\b[^>]*>',re.IGNORECASE)
            self.field_name_re = re.compile(r'\bname=(\'|"|)(?P<name>.+?)(\'|"|)\b',re.IGNORECASE)

    def process_request(self,req):
        """Interpret POST variables that indicate fake file uploads."""
        #  Bail out if any real files were uploaded
#        if len(req.FILES) > 0:
#            return None
        #  Find any post variables named like "fakefile_*".
        #  These contain the fake files that are to be uploaded.
        fakefiles = []
        for (k,v) in req.POST.iteritems():
            if k.startswith(self.field_name):
                if v == "": continue
                fakefiles.append((k[len(self.field_name):],self.file_spec[v]))
        if not fakefiles:
            return None
        #  Remove the fakefile keys from POST
        for f in fakefiles:
            del req.POST[self.field_name + f[0]]
        #  Construct a fake request body and META object
        fake_data = FakeFilesData(fakefiles)
        fake_meta = MergeDict(fake_data.META,req.META)
        #  Re-parse the fake data, triggering upload handlers etc.
        parser = MultiPartParser(fake_meta,fake_data,req.upload_handlers,req.encoding)
        (_, req._files) = parser.parse()

    def process_response(self,req,resp):
        """Augment file upload fields with a fakefile hidden field."""
        if not self.rewrite_response:
            return resp
        if resp.status_code != 200:
            return resp
        ct = resp["Content-Type"].lower()
        if not ct.startswith("text") and not "html" in ct:
            return resp
        resp.content = self.file_field_re.sub(self._add_fakefile,resp.content)
        return resp

    def _add_fakefile(self,match):
        """Insert hidden fakefile field in front of matched file field."""
        field = match.group()
        m = self.field_name_re.search(field)
        if not m:
            return field
        name = self.field_name + m.group("name")
        return "<input type='hidden' name='%s' />%s" % (name,field)


class FakeFilesData:
    """Class representing fake file upload data.

    This class provides a readable file-like represenation of the fake
    upload files, encoded in multipart/form-data format.  It also provides
    the attribute 'META' which provides the necessary HTTP headers for the
    fake request.
    """

    def __init__(self,files):
        """FakeFilesData constructor.

        This constructor expects a single argument, a sequence of (name,spec)
        pairs specifying the fake upload files to be encoded.
        """
        #  Determine the MIME encoding boundary
        try:
            boundary = settings.FAKEUPLOAD_MIME_BOUNDARY
        except AttributeError:
            boundary = "----------thisisthemimeboundary"
        #  Construct each encoded file
        self._files = [FakeFileData(f[0],f[1],boundary) for f in files]
        #  Add the end-of-request footer
        footer = StringIO("--%s--\r\n" % (boundary,))
        footer.size = len(footer.getvalue())
        self._files.append(footer)
        #  Construct the request headers
        size = sum([f.size for f in self._files])
        type = "multipart/form-data; boundary=%s" % (boundary,)
        self.META = {"HTTP_CONTENT_LENGTH":size,"HTTP_CONTENT_TYPE":type}
        #  Internal read-ahead buffer
        self._buffer = ""

    def read(self,size=-1):
        """Read 'size' bytes from the encoded file data."""
        # This method does internal read-ahead buffering, so that the
        # individual encoded files are free to return more or less data than
        # was actually requested.  This makes the implementation of streaming,
        # sleeps etc much easier.
        data = [self._buffer]
        if size < 0:
            #  We want all the remaining data
            for f in self._files:
                ln = f.read()
                while ln != "":
                    data.append(ln)
                    ln = f.read()
            self._files = []
            return "".join(data)
        else:
            #  We want a specific amount
            count = len(data[0])
            while count < size and self._files:
                ln = self._files[0].read(size-count)
                if ln == "":
                    self._files.pop(0)
                else:
                    data.append(ln)
                    count += len(ln)
            data = "".join(data)
            self._buffer = data[size:]
            return data[:size]


class FakeFileData:
    """Class representing a single fake file upload.

    This class provides a readable file-like interface to a single fake]
    upload file, encoded in multipart/form-data format.  However, the 'read'
    method of this object is not guaranteed to return the requested number
    of bytes; either more or less bytes could potentially be returned.
    """

    def __init__(self,name,spec,boundary):
        """FakeFileData constructor.

        This constructor expects the name of the file field, the spec dict
        specifying the fake file info, and the MIME boundary string.
        """
        self._spec = self._normalize_spec(spec)
        disp = 'Content-Disposition: form-data; name="%s"' % (name,)
        if spec.has_key("filename"):
            disp = disp + '; filename="%s"' % (spec["filename"],)
        self._header = "\r\n".join(["--"+boundary,disp,"\r\n"])
        self.size = self._spec['size'] + len(self._header)

    def read(self,size=-1):
        """Read approximately 'size' bytes of encoded data.

        To make it easier to implement streaming, sleeping, etc, this method
        may not return precisely the specified number of bytes; either more
        or less bytes can potentially be returned.
        """
        if self._header:
            header = self._header
            self._header = ""
            return header
        if self._spec.has_key("sleep_time"):
            time.sleep(self._spec["sleep_time"])
        if self._spec.has_key("chunk_size"):
            return self._spec["fileobj"].read(self._spec["chunk_size"])
        return self._spec["fileobj"].read(size)

    def _normalize_spec(self,spec):
        """Create a normalised copy of the given fake file spec.

        This copies the given spec so that it can be freely modified, then
        ensures that it has the following keys:

            * fileobj:  the file object to read data from
            * size:     the size of the file, in bytes

        """
        spec = spec.copy()
        #  Contents provided as a string
        if spec.has_key("contents"):
            spec["fileobj"] = StringIO(spec["contents"])
            spec["size"] = len(spec["contents"])
        #  Contents provided as a file
        elif spec.has_key("file"):
            f = open(spec["file"],"rb")
            f.seek(0,2)
            spec["size"] = f.tell()
            f.seek(0,0)
            spec["fileobj"] = f
        else:
            raise ValueError("Invalid file spec: " + repr(spec))
        return spec

