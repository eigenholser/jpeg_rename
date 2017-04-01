
class FileMapList(object):
    """
    Intelligently add FileMap() instances to file_map list based on order of
    instance.new_fn attributes.
    """

    def __init__(self):
        self.file_map = []

    def add(self, instance):
        """
        Add, whether insert or append, a FileMap instance to the file_map list
        in the order of instance.new_fn. If there are duplicate new_fn in the
        list, they will be resolved in instance.move().
        """
        index = 0
        inserted = False
        for fm in self.file_map:
            if instance.new_fn < fm.new_fn:
                self.file_map.insert(index, instance)
                inserted = True
                break
            index += 1

        # Reached end of list with no insert. Append to list instead.
        if not inserted:
            self.file_map.append(instance)

    def get(self):
        """
        Define a generator function here to return items on the file_map
        list.
        """
        return (x for x in self.file_map)
