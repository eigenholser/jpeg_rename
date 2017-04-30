import re
import photo_rename


class OrderedListMixin(object):
    """
    Mixin implementing the logic for FileList and FilemapList.
    """

    def __init__(self):
        self.list = []

    def add(self, obj):
        index = 0
        inserted = False

        if type(obj) is str:
            add = obj
        else:
            add = obj.new_fn

        for elem in self.get():
            if type(elem) is str:
                cmp = elem
            else:
                cmp = elem.new_fn

            # Since file.jpg > file-1.jpg True and file-1.jpg < file-2.jpg
            # we must compare because we want ordering :
            #   file.jpg, file-1.jpg, file-2.jpg

            # Compare add of the form YYYYmmDD_HHMMSS*
            madd = re.match(r"^\d{8}_\d{6}", add)
            mcmp = re.match(r"^\d{8}_\d{6}", cmp)
            if (madd and mcmp) and (madd.group(0) == mcmp.group(0)):
                if (not re.search(r"-\d+\.", add) and
                        re.search(r"-\d+\.", cmp)):
                    #if add > cmp:
                    self.list.insert(index, obj)
                    inserted = True
                    break
                if (re.search(r"-\d+\.", add) and re.search(r"-\d+\.", cmp)):
                    if add < cmp:
                        self.list.insert(index, obj)
                        inserted = True
                        break
            else:
                # Everything else compares normally.
                if add < cmp:
                    self.list.insert(index, obj)
                    inserted = True
                    break
            index += 1

        # Reached end of list with no insert. Append to list instead.
        if not inserted:
            self.list.append(obj)

    def get(self):
        """
        Define a generator function here to return items on the list.
        list.
        """
        return (obj for obj in self.list)


@photo_rename.logged_class
class FileList(OrderedListMixin):
    """
    Ordered list of files.
    """


@photo_rename.logged_class
class FilemapList(OrderedListMixin):
    """
    Ordered list of filemap instances.
    """
