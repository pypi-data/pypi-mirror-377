import os
import uuid
import time
from datetime import datetime
import warnings
from .core_sina import KoshSinaObject, kosh_pickler
from .utils import get_graph
from .utils import compute_fast_sha
from .utils import compute_long_sha
from .utils import cleanup_sina_record_from_kosh_sync
from .utils import update_json_file_with_records_and_relationships
from .utils import __check_valid_connection_type__
from . import lock_strategies
import kosh
import six
try:
    import orjson
except ImportError:
    import json as orjson  # noqa
try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable


class KoshDataset(KoshSinaObject):
    def __init__(self, id, store, schema=None, record=None, kosh_type=None):
        """KoshSinaDataset Sina representation of Kosh Dataset

        :param id: dataset's unique Id
        :type id: str
        :param store: store containing the dataset
        :type store: KoshSinaStore
        :param schema: Kosh schema validator
        :type schema: KoshSchema
        :param record: to avoid looking up in sina pass sina record
        :type record: Record
        :param kosh_type: type of Kosh object (dataset, file, project, ...)
        :type kosh_type: str
        """
        with store.lock_strategy:
            if kosh_type is None:
                kosh_type = store._dataset_record_type
            super(KoshDataset, self).__init__(id, kosh_type=kosh_type,
                                              protected=[
                                                "__name__", "__creator__", "__store__",
                                                "_associated_data_", "__features__",
                                                "__creation_date__"],
                                              record_handler=store.__record_handler__,
                                              store=store, schema=schema, record=record)
            self.__dict__["__record_handler__"] = store.__record_handler__
            if record is None:
                record = self.get_record()
            try:
                self.__dict__["__creator__"] = record["data"]["creator"]["value"]
            except Exception:
                pass
            try:
                self.__dict__["__creation_date__"] = record["data"]["creation_date"]["value"]
            except Exception:
                pass
            try:
                self.__dict__["__name__"] = record["data"]["name"]["value"]
            except Exception:
                pass
            if schema is not None or "schema" in record["data"]:
                self.validate()

    @lock_strategies.lock_method
    def __str__(self):
        """string representation"""
        import reprlib
        if self.__store__.verbose_attributes:
            def reprtool(item):
                return item
        else:
            def reprtool(item):
                if isinstance(item, str):
                    return reprlib.repr(item)[1:-1]
                else:
                    return reprlib.repr(item)
        st = ""
        st += "KOSH DATASET\n"
        st += "\tid: {}\n".format(self.id)
        try:
            st += "\tname: {}\n".format(self.__name__)
        except Exception:
            st += "\tname: ???\n"
        try:
            st += "\tcreator: {}\n".format(self.creator)
        except Exception:
            st += "\tcreator: ???\n"
        try:
            st += "\tcreation date: {}\n".format(self.creation_date)
        except Exception:
            st += "\tcreation date: ???\n"
        try:
            st += "\tlast modified date: {}\n".format(self.last_modified_date)
        except Exception:
            st += "\tlast modified date: ???\n"
        atts = self.__attributes__
        if len(atts) > 0:
            st += "\n--- Attributes ---\n"
            for a in sorted(atts):
                if a == "_associated_data_" or "_ENSEMBLE_TAG_" in a:  # Remove associated data and ensemble tags
                    continue
                if not self.is_ensemble_attribute(a):
                    st += "\t{}: {}\n".format(a, reprtool(atts[a]))
        if self._associated_data_ is not None:
            st += "--- Associated Data ({})---\n".format(
                len(self._associated_data_))
            # Let's organize per mime_type
            associated = {}
            for a in self._associated_data_:
                if a == self.id:
                    st2 = "internal ( {} )".format(
                        ", ".join(self.get_record()["curve_sets"].keys()))
                    if "sina/curve" not in associated:
                        associated["sina/curve"] = [st2, ]
                    else:
                        associated["sina/curve"].append(st2)
                else:
                    if "__uri__" in a:
                        a_id, a_uri = a.split("__uri__")
                        a_mime_type = self.get_record(
                        )["files"][a_uri]["mimetype"]
                    else:
                        a_id, a_uri = a, None
                    a_obj = self.__store__._load(a_id)
                    if a_uri is None:
                        a_uri = a_obj.uri
                        a_mime_type = a_obj.mime_type
                    st2 = "{a_uri} ( {a} )".format(a_uri=a_uri, a=a_id)
                    if a_mime_type not in associated:
                        associated[a_mime_type] = [st2, ]
                    else:
                        associated[a_mime_type].append(st2)
            for mime in sorted(associated):
                st += "\tMime_type: {mime}".format(mime=mime)
                for uri in sorted(associated[mime]):
                    st += "\n\t\t{uri}".format(uri=uri)
                st += "\n"
        ensembles = tuple(self.get_ensembles())
        st += "--- Ensembles ({})---".format(len(ensembles))
        st += "\n\t" + str([str(x.id) for x in ensembles])
        st += "\n--- Ensemble Attributes ---\n"
        for ensemble in ensembles:
            st += "\t--- Ensemble {} ---\n".format(ensemble.id)
            eas = ensemble.list_attributes()
            for ignore in ['creator', 'id', 'name', 'creation_date', 'last_modified_date']:
                eas.remove(ignore)
            eas.sort()
            st += f"\t\t{reprtool(eas)}\n"

            ensemble_tags = self.list_ensemble_tags(ensemble.id)
            ensemble_tags.sort()
            if ensemble_tags:
                ensemble_tags = [et.replace(f"{ensemble.id}_ENSEMBLE_TAG_", "") for et in ensemble_tags]
                st += "\t\t--- Ensemble Tags ---\n"
                st += f"\t\t\t{ensemble_tags}\n"
        if self.alias_feature is not {}:
            st += '--- Alias Feature Dictionary ---'
            for key, val in self.alias_feature.items():
                st += f"\n\t{key}: {val}"
        return st

    @lock_strategies.lock_method
    def _repr_pretty_(self, p, cycle):
        """Pretty display in Ipython"""
        p.text(self.__str__())

    @lock_strategies.lock_method
    def cleanup_files(self, dry_run=False, interactive=False,
                      clean_fastsha=False, **search_keys):
        """Cleanup the dataset from references to dead files
        Also updates the fast_shas if necessary
        You can filter associated objects by passing key=values
        e.g mime_type=hdf5 will only dissociate non-existing files associated with mime_type hdf5
        some_att=some_val will only dissociate non-existing files associated and having the attribute
        'some_att' with value of 'some_val'
        returns list of uris to be removed.
        :param dry_run: Only does a dry_run
        :type dry_run: bool
        :param interactive: interactive mode, ask before dissociating
        :type interactive: bool
        :param clean_fastsha: Do we want to update fast_sha if it changed?
        :type clean_fastsha: bool
        :returns: list of uris (to be) removed or updated
        :rtype: list
        """
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write'])
        bads = []
        for associated in self.find(**search_keys):
            clean = 'n'
            if not os.path.exists(associated.uri):  # Ok this is gone
                bads.append(associated.uri)
                if dry_run:  # Dry run
                    clean = 'n'
                elif interactive:
                    clean = input("\tDo you want to dissociate {} (mime_type: {})? [Y/n]".format(
                        associated.uri, associated.mime_type)).strip()
                    if len(clean) > 0:
                        clean = clean[0]
                        clean = clean.lower()
                    else:
                        clean = 'y'
                else:
                    clean = 'y'
                if clean == 'y':
                    self.dissociate(associated.uri)
            elif clean_fastsha:
                # file still exists
                # We might want to update its fast sha
                fast_sha = compute_fast_sha(associated.uri)
                if fast_sha != associated.fast_sha:
                    bads.append(associated.uri)
                    if dry_run:  # Dry run
                        clean = 'n'
                    elif interactive:
                        clean = input("\tfast_sha for {} seems to have changed from {}"
                                      " to {}, do you wish to update?".format(
                                          associated.uri, associated.fast_sha, fast_sha))
                        if len(clean) > 0:
                            clean = clean[0]
                            clean = clean.lower()
                        else:
                            clean = 'y'
                    else:
                        clean = "y"
                    if clean == "y":
                        associated.fast_sha = fast_sha
        return bads

    @lock_strategies.lock_method
    def check_integrity(self):
        """Runs a sanity check on the dataset:
        1- Are associated files reachable?
        2- Did fast_shas change since file was associated
        """
        return self.cleanup_files(dry_run=True, clean_fastsha=True)

    @lock_strategies.lock_method
    def open(self, Id=None, loader=None, *args, **kargs):
        """open an object associated with a dataset

        :param Id: id of object to open, defaults to None which means first one.
        :type Id: str, optional
        :param loader: loader to use for this object, defaults to None
        :type loader: KoshLoader, optional
        :raises RuntimeError: object id not associated with dataset
        :return: object ready to be used
        """
        if Id is None:
            if len(self._associated_data_) > 0:
                Id = self._associated_data_[0]
            else:
                for Id in self._associated_data_:
                    return self.__store__.open(Id, loader)
        elif Id not in self._associated_data_:
            raise RuntimeError(
                "object {Id} is not associated with this dataset".format(
                    Id=Id))
        return self.__store__.open(Id, loader, *args, **kargs)

    @lock_strategies.lock_method
    def list_features(self, Id=None, loader=None,
                      use_cache=True, verbose=False, *args, **kargs):
        """list_features list features available if multiple associated data lead to duplicate feature name
        then the associated_data uri gets appended to feature name

        :param Id: id of associated object to get list of features from, defaults to None which means all
        :type Id: str, optional
        :param loader: loader to use to search for feature, will return ONLY features that the loader knows about
        :type loader: kosh.loaders.KoshLoader
        :param use_cache: If features is found on cache use it (default: True)
        :type use_cache: bool
        :param verbose: Verbose mode will show which file is being opened and errors on it
        :type verbose: bool
        :raises RuntimeError: object id not associated with dataset
        :return: list of features available
        :rtype: list
        """
        # Ok no need to sync any of this we will not touch the code
        saved_sync = self.__store__.is_synchronous()
        if saved_sync:
            # we will not update any rec in here, turning off sync
            # it makes things much faster
            backup = self.__store__.__sync__dict__
            self.__store__.__sync__dict__ = {}
            self.__store__.synchronous()
        features = []
        loaders = []
        associated_data = self._associated_data_
        if Id is None:
            for associated in associated_data:
                if verbose:
                    asso = self.__store__._load(associated)
                    print("Finding features for {}".format(asso))
                if loader is None:
                    ld, _ = self.__store__._find_loader(associated,
                                                        requestorId=self.id, verbose=verbose, use_cache=use_cache)
                else:
                    if (associated, self.id) not in self.__store__._cached_loaders:
                        self.__store__._cached_loaders[associated, self.id] = loader(
                            self.__store__._load(associated), requestorId=self.id), None
                        # self.__store__.update_cached_loaders()
                    ld, _ = self.__store__._cached_loaders[associated, self.id]
                loaders.append(ld)
                try:
                    features += ld._list_features(*
                                                  args, use_cache=use_cache, **kargs)
                except Exception as err:  # Ok the loader couldn't get the feature list
                    if verbose:
                        print("\tCould not obtain features from loader {}\n\t\tError:{}".format(loader, err))
            if len(features) != len(set(features)):
                # duplicate features we need to redo
                # Adding uri to feature name
                ided_features = []
                for index, associated in enumerate(associated_data):
                    ld = loaders[index]
                    if ld is None:
                        continue
                    asso = self.__store__._load(associated)
                    these_features = ld._list_features(
                        *args, use_cache=use_cache, **kargs)
                    for feature in these_features:
                        if features.count(feature) > 1:  # duplicate
                            ided_features.append(
                                "{feature}_@_{uri}".format(feature=feature, uri=asso.uri))
                        else:  # not duplicate name
                            ided_features.append(feature)
                features = ided_features
        elif Id not in self._associated_data_:
            raise RuntimeError(
                "object {Id} is not associated with this dataset".format(
                    Id=Id))
        else:
            if loader is not None:
                ld = loader
            else:
                ld, _ = self.__store__._find_loader(Id, requestorId=self.id, verbose=verbose)
            features = ld._list_features(*args, use_cache=use_cache, verbose=verbose, **kargs)
        features_id = self.__features__.get(Id, {})
        features_id[loader] = features
        self.__features__[Id] = features_id
        if saved_sync:
            # we need to restore sync mode
            self.__store__.__sync__dict__ = backup
            self.__store__.synchronous()
        return features

    @lock_strategies.lock_method
    def get_execution_graph(self, feature=None, Id=None,
                            loader=None, transformers=[], use_cache=True, *args, **kargs):
        """get data for a specific feature
        :param feature: feature (variable) to read, defaults to None
        :type feature: str, optional if loader does not require this
        :param Id: object to read in, defaults to None
        :type Id: str, optional
        :param loader: loader to use to get data,
                       defaults to None means pick for me
        :type loader: kosh.loaders.KoshLoader
        :param transformers: A list of transformers to use after the data is loaded
        :type transformers: kosh.transformer.KoshTranformer
        :param use_cache: use cache to find features
        :type use_cache: bool
        :returns: [description]
        :rtype: [type]
        """
        if feature is None:
            out = []
            for feat in self.list_features():
                out.append(self.get_execution_graph(Id=None,
                                                    feature=feat,
                                                    format=format,
                                                    loader=loader,
                                                    transformers=transformers,
                                                    *args, **kargs))
            return out
        # Need to make sure transformers are a list
        if not isinstance(transformers, Iterable):
            transformers = [transformers, ]
        # we need to figure which associated data has the feature
        if not isinstance(feature, list):
            features = [feature, ]
        else:
            features = feature
        possibles = {}
        inter = None
        union = set()

        alias_feature = self.alias_feature
        alias_feature_flattened = [[]] * len(alias_feature)
        for i, (key, val) in enumerate(alias_feature.items()):
            alias_feature_flattened[i] = [key]
            if isinstance(val, list):
                alias_feature_flattened[i].extend(val)
            elif isinstance(val, str):
                alias_feature_flattened[i].extend([val])

        def find_features(self, a, use_cache=True):

            a_original = a

            if "__uri__" in a:
                # Ok this is a pure sina file with mime_type
                a, _ = a.split("__uri__")
            a_obj = self.__store__._load(a)
            if loader is None:
                ld, _ = self.__store__._find_loader(a_original, requestorId=self.id, use_cache=use_cache)
                if ld is None:  # unknown mimetype probably
                    return _, None, _, _
            else:
                if a_obj.mime_type in loader.types:
                    ld = loader(a_obj, requestorId=self.id)
                else:
                    return _, None, _, _

            # Dataset with curve have themselves as uri
            obj_uri = getattr(ld.obj, "uri", "self")
            ld_features = ld._list_features(use_cache=use_cache)

            return a_original, ld, obj_uri, ld_features

        for index, feature_ in enumerate(features):
            possible_ids = []
            if Id is None:
                for a in self._associated_data_:

                    a_original, ld, obj_uri, ld_features = find_features(self, a, use_cache=use_cache)
                    if ld is None:  # No features
                        continue

                    if isinstance(ld, kosh.loaders.core.KoshSinaLoader):
                        # ok we have to be careful list_features can be returned two ways
                        if isinstance(ld_features[0], (list, tuple)) and isinstance(feature_, six.string_types):
                            # we need to convert the feature to str
                            possibilities = kosh.utils.find_curveset_and_curve_name(feature_, self.get_record())
                            if len(possibilities) > 1:
                                raise ValueError("cannot uniquely pinpoint {}, could be one of {}".format(
                                    feature_, possibilities))
                            feature_ = possibilities[0]
                            features[index] = feature_
                        elif isinstance(ld_features[0], six.string_types) and isinstance(feature_, (list, tuple)):
                            feature_ = "/".join(feature_)
                            features[index] = feature_

                    if ("_@_" not in feature_ and (feature_ in ld_features or list(feature_) in ld_features)) or\
                            feature_ is None or\
                            (feature_[:-len(obj_uri) - 3] in ld_features and
                             feature_[-len(obj_uri):] == obj_uri):
                        possible_ids.append(a_original)
                if possible_ids == []:  # All failed but could be something about the feature
                    found = False
                    if alias_feature_flattened:
                        feature_original = feature_
                        af = []
                        for af_list in alias_feature_flattened:
                            if feature_.split("/")[-1] in af_list:
                                af = af_list
                                if feature_ in af_list:
                                    af.remove(feature_)
                                break

                        poss = []
                        for a in self._associated_data_:

                            a_original, ld, obj_uri, ld_features = find_features(self, a, use_cache=use_cache)
                            if ld is None:  # No features
                                continue

                            for ld in ld_features:

                                if ld.split('/')[-1] in af or ld in af:

                                    found = True
                                    feature_ = ld
                                    features[index] = ld
                                    possible_ids.append(a_original)
                                    poss.append(ld)

                        if len(poss) > 1:
                            raise ValueError("Cannot uniquely pinpoint {}, could be one of {}"
                                             .format(feature_original, poss))
                    if not found:
                        raise ValueError("Cannot find feature {} in dataset"
                                         .format(feature_))
            elif Id == self.id:
                # Ok asking for data not associated externally
                # Likely curve
                ld, _ = self.__store__._find_loader(Id, requestorId=self.id, use_cache=use_cache)
                if feature_ in ld._list_features(use_cache=use_cache):
                    possible_ids = [Id, ]
                else:  # ok not a curve maybe a file?
                    rec = self.get_record()
                    for uri in rec["files"]:
                        if "mimetype" in rec["files"][uri]:
                            full_id = "{}__uri__{}".format(Id, uri)
                            ld, _ = self.__store__._find_loader(full_id, requestorId=self.id, use_cache=use_cache)
                            if ld is not None and feature_ in ld._list_features(use_cache=use_cache):
                                possible_ids = [full_id, ]
            elif Id not in self._associated_data_:
                raise RuntimeError(
                    "object {Id} is not associated with this dataset".format(
                        Id=Id))
            else:
                possible_ids = [Id, ]
            if inter is None:
                inter = set(possible_ids)
            else:
                inter = inter.intersection(set(possible_ids))
            union = union.union(set(possible_ids))
            possibles[feature_] = possible_ids

        if len(inter) != 0:
            union = inter

        ids = {}
        # Now let's go through each possible uri
        # and group features in them
        for id_ in union:
            matching_features = []
            for feature_ in features:
                if feature_ in possibles and id_ in possibles[feature_]:
                    matching_features.append(feature_)
                    del possibles[feature_]
            if len(matching_features) > 0:
                ids[id_] = matching_features

        out = []
        for id_ in ids:
            features = ids[id_]
            for Id in possible_ids:
                tmp = None
                try:
                    if loader is None:
                        ld, _ = self.__store__._find_loader(Id, requestorId=self.id, use_cache=use_cache)
                        mime_type = ld._mime_type
                    else:
                        if (Id, self.id) not in self.__store__._cached_loaders:
                            a_obj = self.__store__._load(Id)
                            self.__store__._cached_loaders[Id, self.id] = loader(a_obj, requestorId=self.id)
                            # self.__store__.update_cached_loaders()
                            mime_type = a_obj.mime_type
                        ld = self.__store__._cached_loaders[Id, self.id]
                    # Essentially make a copy
                    # Because we want to attach the feature to it
                    # But let's not lose the cached list_features
                    ld_uri = getattr(ld, "uri", None)
                    ld = ld.__class__(
                        ld.obj, mime_type=ld._mime_type, uri=ld_uri, requestorId=self.id)
                    # Ensures there is a possible path to format
                    get_graph(mime_type, ld, transformers)
                    final_features = []
                    obj_uri = getattr(ld.obj, "uri", "")
                    for feature_ in features:
                        if (feature_[:-len(obj_uri) - 3] in ld._list_features(use_cache=use_cache)
                                and feature_[-len(obj_uri):] == obj_uri):
                            final_features.append(
                                feature_[:-len(obj_uri) - 3])
                        else:
                            final_features.append(feature_)
                    if len(final_features) == 1:
                        final_features = final_features[0]
                    tmp = ld.get_execution_graph(final_features,
                                                 transformers=transformers
                                                 )
                    ld.feature = final_features
                    ExecGraph = kosh.exec_graphs.KoshExecutionGraph(tmp)
                except Exception:
                    import traceback
                    traceback.print_exc()
                    ExecGraph = kosh.exec_graphs.KoshExecutionGraph(tmp)
                out.append(ExecGraph)

        if len(out) == 1:
            return out[0]
        else:
            return out

    @lock_strategies.lock_method
    def get(self, feature=None, format=None, Id=None, loader=None,
            group=False, transformers=[], *args, **kargs):
        """get data for a specific feature
        :param feature: feature (variable) to read, defaults to None
        :type feature: str, optional if loader does not require this
        :param format: desired format after extraction
        :type format: str
        :param Id: object to read in, defaults to None
        :type Id: str, optional
        :param loader: loader to use to get data,
                       defaults to None means pick for me
        :type loader: kosh.loaders.KoshLoader
        :param group: group multiple features in one get call, assumes loader can handle this
        :type group: bool
        :param transformers: A list of transformers to use after the data is loaded
        :type transformers: kosh.transformer.KoshTranformer
        :raises RuntimeException: could not get feature
        :raises RuntimeError: object id not associated with dataset
        :returns: [description]
        :rtype: [type]
        """
        G = self.get_execution_graph(
            feature=feature,
            Id=Id,
            loader=loader,
            transformers=transformers,
            *args,
            **kargs)
        if isinstance(G, list):
            return [g.traverse(format=format, *args, **kargs) for g in G]
        else:
            return G.traverse(format=format, *args, **kargs)

    @lock_strategies.lock_method
    def __getitem__(self, feature):
        """Shortcut to access a feature or list of
        :param feature: feature(s) to access in dataset
        :type feature: str or list of str
        :returns: (list of) access point to feature requested
        :rtype: (list of) kosh.execution_graph.KoshIoGraph
        """
        return self.get_execution_graph(feature)

    @lock_strategies.lock_method
    def __dir__(self):
        """__dir__ list functions and attributes associated with dataset
        :return: functions, methods, attribute associated with this dataset
        :rtype: list
        """
        current = set(super(KoshDataset, self).__dir__())
        try:
            atts = set(self.listattributes() + self.__protected__)
        except Exception:
            atts = set()
        return list(current.union(atts))

    @lock_strategies.lock_method
    def reassociate(self, target, source=None, absolute_path=True):
        """This function allows to re-associate data whose uri might have changed

        The source can be the original uri or sha and target is the new uri to use.
        :param target: New uri
        :type target: str
        :param source: uri or sha (long or short of reassociate)
                       to reassociate with target, if None then the short uri from target will be used
        :type source: str or None
        :param absolute_path: if file exists should we store its absolute_path
        :type absolute_path: bool
        :return: None
        :rtype: None
        """
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write'])
        self.__store__.reassociate(target, source=source, absolute_path=absolute_path)

    @lock_strategies.lock_method
    def validate(self):
        """If dataset has a schema then make sure all attributes pass the schema"""
        if self.schema is not None:
            self.schema.validate(self)

    @lock_strategies.lock_method
    def searchable_source_attributes(self):
        """Returns all the attributes of associated sources
        :return: List of all attributes you can use to search sources in the dataset
        :rtype: set
        """
        searchable = set()
        for source in self.find():
            searchable = searchable.union(source.listattributes())
        return searchable

    @lock_strategies.lock_method
    def describe_feature(self, feature, Id=None, **kargs):
        """describe a feature

        :param feature: feature (variable) to read, defaults to None
        :type feature: str, optional if loader does not require this
        :param Id: id of associated object to get list of features from, defaults to None which means all
        :type Id: str, optional
        :param kargs: keywords to pass to list_features (optional)
        :type kargs: keyword=value
        :raises RuntimeError: object id not associated with dataset
        :return: dictionary describing the feature
        :rtype: dict
        """
        loader = None
        if Id is None:
            for a in self._associated_data_:
                ld, _ = self.__store__._find_loader(a, requestorId=self.id)
                if feature in ld._list_features(**kargs) or \
                        (feature[:-len(ld.obj.uri) - 3] in ld._list_features()
                         and feature[-len(ld.obj.uri):] == ld.obj.uri):
                    loader = ld
                    break
        elif Id not in self._associated_data_:
            raise RuntimeError(
                "object {Id} is not associated with this dataset".format(
                    Id=Id))
        else:
            loader, _ = self.__store__._find_loader(Id, requestorId=self.id)
        return loader.describe_feature(feature)

    @lock_strategies.lock_method
    def dissociate(self, uri, absolute_path=True):
        """dissociates a uri/mime_type with this dataset

        :param uri: uri to access file
        :type uri: str
        :param absolute_path: if file exists should we store its absolute_path
        :type absolute_path: bool
        :return: None
        :rtype: None
        """
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write'])
        if absolute_path and os.path.exists(uri):
            uri = os.path.abspath(uri)
        rec = self.get_record()
        if uri not in rec["files"]:
            # Not associated with this uri anyway
            return
        kosh_id = str(rec["files"][uri]["kosh_id"])
        del rec["files"][uri]
        now = time.time()
        rec["user_defined"]['kosh_information']["{uri}___associated_last_modified".format(
            uri=uri)] = now
        if self.__store__.__sync__:
            self._update_record(rec)
        # Get all object that have been associated with this uri
        rec = self.get_record(kosh_id)
        associated_ids = rec.data.get("associated", {"value": []})["value"]
        associated_ids.remove(self.id)
        rec.data["associated"]["value"] = associated_ids
        if self.__store__.__sync__:
            self._update_record(rec)
        else:
            self._update_record(rec, self.__store__._added_unsync_mem_store)
        if len(associated_ids) == 0:  # ok no other object is associated
            self._update_record(kosh_id, delete=True)
            if (kosh_id, self.id) in self.__store__._cached_loaders:
                del self.__store__._cached_loaders[kosh_id, self.id]
            if (kosh_id, None) in self.__store__._cached_loaders:
                del self.__store__._cached_loaders[kosh_id, None]
            # We also need to clean up all features associated with the id
            cached_features = self.__store__._cached_features_
            yank = []
            for id in cached_features:
                if id.endswith(uri):
                    yank.append(id)
            for id in yank:
                del cached_features[id]
            self.__store__._cached_features_ = cached_features

        # Since we changed the associated, we need to cleanup
        # the features cache
        self.__features__[None] = {}
        self.__features__[kosh_id] = {}

    @lock_strategies.lock_method
    def associate(self, uri, mime_type, metadata={},
                  id_only=None, long_sha=False, absolute_path=True,
                  loader_kwargs=None, preload_features=False):
        """associates a uri/mime_type with this dataset

        :param uri: uri(s) to access content
        :type uri: str or list of str
        :param mime_type: mime type associated with this file
        :type mime_type: str or list of str
        :param metadata: metadata to associate with file, defaults to {}
        :type metadata: dict, optional
        :param id_only: do not return kosh file object (None and default), just its id (True)
                        or the KoshSinaFile (False)
        :type id_only: bool or None
        :param long_sha: Do we compute the long sha on this or not?
        :type long_sha: bool
        :param absolute_path: if file exists should we store its absolute_path
        :type absolute_path: bool
        :param loader_kwargs: Extra arguments to pass to more advanced loader
        :type loader_kwargs: dict, optional
        :param preload_features: runs list_features on associated uri to save time in future reads (default: False)
        :type preload_features: bool
        :return: A (list) Kosh Sina File(s)
        :rtype: list of KoshSinaFile or KoshSinaFile
        """
        from sina.model import Record
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write', 'append'])
        rec = self.get_record()
        # Need to remember we touched associated files
        now = time.time()

        if loader_kwargs is not None:
            pickled = kosh_pickler.dumps(loader_kwargs)
            metadata['loader_kwargs'] = pickled

        if isinstance(uri, six.string_types):
            uris = [uri, ]
            metadatas = [metadata, ]
            mime_types = [mime_type, ]
            single_element = True
        else:
            uris = uri
            if isinstance(metadata, dict):
                metadatas = [metadata, ] * len(uris)
            else:
                metadatas = metadata
            if isinstance(mime_type, six.string_types):
                mime_types = [mime_type, ] * len(uris)
            else:
                mime_types = mime_type
            single_element = False

        new_recs = []
        updated_recs = []
        kosh_file_ids = []

        for i, uri in enumerate(uris):
            try:
                meta = metadatas[i].copy()
                if os.path.exists(uri):
                    if long_sha:
                        meta["long_sha"] = compute_long_sha(uri)
                    if absolute_path:
                        uri = os.path.abspath(uri)
                    if not os.path.isdir(uri) and "fast_sha" not in meta:
                        meta["fast_sha"] = compute_fast_sha(uri)
                try:
                    rec["user_defined"]['kosh_information']["{uri}___associated_last_modified".format(
                        uri=uri)] = now
                except KeyError:  # Sina records will not have this
                    rec["user_defined"]['kosh_information'] = {}
                    rec["user_defined"]['kosh_information']["{uri}___associated_last_modified".format(
                        uri=uri)] = now
                # We need to check if the uri was already associated somewhere
                tmp_uris = list(self.__store__.find(
                    types=[self.__store__._sources_type, ], uri=uri, ids_only=True))

                if len(tmp_uris) == 0:
                    Id = uuid.uuid4().hex
                    rec_obj = Record(id=Id, type=self.__store__._sources_type, user_defined={'kosh_information': {}})
                    new_recs.append(rec_obj)
                else:
                    rec_obj = self.get_record(tmp_uris[0])
                    Id = rec_obj.id
                    existing_mime = rec_obj["data"]["mime_type"]["value"]
                    mime_type = mime_types[i]
                    if existing_mime != mime_types[i]:
                        rec["files"][uri]["mime_type"] = existing_mime
                        raise TypeError("source {} is already associated with another dataset with mimetype"
                                        " '{}' you specified mime_type '{}'".format(uri, existing_mime, mime_types[i]))
                    updated_recs.append(rec_obj)
                rec.add_file(uri, mime_types[i])
                rec["files"][uri]["kosh_id"] = Id
                meta["uri"] = uri
                meta["mime_type"] = mime_types[i]
                associated = rec_obj["data"].get(
                    "associated", {'value': []})["value"]
                associated.append(self.id)
                meta["associated"] = associated
                for key in meta:
                    if key not in rec_obj.data:
                        rec_obj.add_data(key, meta[key])
                    else:
                        rec_obj["data"][key]["value"] = meta[key]
                    last_modif_att = "{name}_last_modified".format(name=key)
                    rec_obj["user_defined"]['kosh_information'][last_modif_att] = time.time()
                if not self.__store__.__sync__:
                    rec_obj.set_data("last_modified_date", str(datetime.fromtimestamp(time.time())))
                    self.__store__.__sync__dict__[Id] = rec_obj
            except TypeError as err:
                raise err
            except Exception:
                # file already in there
                # Let's get the matching id
                if rec_obj["data"]["mime_type"]["value"] != mime_types[i]:
                    raise TypeError("file {} is already associated with this dataset with mimetype"
                                    " '{}' you specified mime_type '{}'".format(uri, existing_mime, mime_type))
                else:
                    Id = rec["files"][uri]["kosh_id"]
                    if len(metadatas[i]) != 0:
                        warnings.warn(
                            "uri {} was already associated, metadata will "
                            "stay unchanged\nEdit object (id={}) directly to update attributes.".format(uri, Id))
            kosh_file_ids.append(Id)

        if self.__store__.__sync__:
            self._update_record(new_recs)
            self._update_record(rec)
            self._update_record(updated_recs)
        else:
            self._update_record(rec, self.__store__._added_unsync_mem_store)
            self._update_record(updated_recs, self.__store__._added_unsync_mem_store)

        # Since we changed the associated, we need to cleanup
        # the features cache
        self.__features__[None] = {}
        # Let's rerun the list_features now so it's cached in the store and for the dataset.
        if preload_features:
            self.list_features()

        if id_only is None:
            return

        if id_only:
            if single_element:
                return kosh_file_ids[0]
            else:
                return kosh_file_ids

        kosh_files = []
        for Id in kosh_file_ids:
            self.__features__[Id] = {}
            kosh_file = KoshSinaObject(Id=Id,
                                       kosh_type=self.__store__._sources_type,
                                       store=self.__store__,
                                       metadata=metadata,
                                       record_handler=self.__record_handler__)
            kosh_files.append(kosh_file)

        if single_element:
            return kosh_files[0]
        else:
            return kosh_files

    @lock_strategies.lock_method
    def search(self, *atts, **keys):
        """
        Deprecated use find
        """
        warnings.warn("The 'search' function is deprecated and now called `find`.\n"
                      "Please update your code to use `find` as `search` might disappear in the future",
                      DeprecationWarning)
        return self.find(*atts, **keys)

    @lock_strategies.lock_method
    def find(self, *atts, **keys):
        """find associated data matching some metadata
        arguments are the metadata name we are looking for e.g
        find("attr1", "attr2")
        you can further restrict by specifying exact value for a metadata
        via key=value
        you can return ids only by using: ids_only=True
        range can be specified via: sina.utils.DataRange(min, max)

        "file_uri" is a special key that will return the kosh object associated
        with this dataset for the given uri.  e.g store.find(file_uri=uri)

        :return: list of matching objects associated with dataset
        :rtype: list
        """
        from sina.utils import exists

        if self._associated_data_ is None:
            return
        sina_kargs = {}
        ids_only = keys.pop("ids_only", False)
        load_type = keys.pop("load_type", "source")
        # We are only interested in ids from Sina
        sina_kargs["ids_only"] = True

        inter_recs = self._associated_data_
        tag = "{}__uri__".format(self.id)
        tag_len = len(tag)
        virtuals = [x[tag_len:] for x in inter_recs if x.startswith(tag)]
        # Bug in sina 1.10.0 forces us to remove the virtual from the pool
        for v_id in virtuals:
            inter_recs.remove("{}{}".format(tag, v_id))
        if "file" in sina_kargs and "file_uri" in sina_kargs:
            raise ValueError(
                "The `file` keyword is being deprecated for `file_uri` you cannot use both")
        if "file" in sina_kargs:
            warnings.warn(
                "The `file` keyword has been renamed `file_uri` and may not be available in future versions",
                DeprecationWarning)
            file_uri = sina_kargs.pop("file")
            sina_kargs["file_uri"] = file_uri

        # The data dict for sina
        keys.pop("id_pool", None)
        sina_kargs["query_order"] = keys.pop(
            "query_order", ("data", "file_uri", "types"))
        sina_data = keys.pop("data", {})
        for att in atts:
            sina_data[att] = exists()
        sina_data.update(keys)
        sina_kargs["data"] = sina_data

        match = set(
            self.__record_handler__.find(
                id_pool=inter_recs,
                **sina_kargs))
        # instantly restrict to associated data
        if not self.__store__.__sync__:
            match_mem = set(self.__store__._added_unsync_mem_store.records.find(
                id_pool=inter_recs, **sina_kargs))
            match = match.union(match_mem)
        # ok now we need to search the data on the virtual datasets
        rec = self.get_record()
        for uri in virtuals:
            file_section = rec["files"][uri]
            tags = file_section.get("tags", [])
            # Now let's search the tags....
            match_it = True
            for key in sina_kargs["data"]:
                if key == "mime_type":
                    if file_section.get("mimetype", file_section.get(
                            "mime_type", None)) != sina_kargs["data"][key]:
                        match_it = False
                        break
                elif key not in tags or sina_kargs["data"][key] != exists():
                    match_it = False
                    break
            if match_it:
                # we can't have a set anymore
                match.add(self.id)

        for rec_id in match:
            # We need to cleanup for "virtual association".
            # e.g comes directly from a sina rec with 'file'/'mimetype' in it.
            rec_id = rec_id.split("__uri__")[0]
            if load_type == 'source':
                yield rec_id if ids_only else self.__store__._load(rec_id)
            elif load_type == 'dictionary':
                yield rec_id if ids_only else self.get_record(rec_id).__dict__['raw']

    @lock_strategies.lock_method
    def export(self, file=None, sina_record=False, output_format='json'):
        """Exports this dataset
        :param file: export dataset to a file
        :type file: None or str
        :param sina_record: filename to export the dataset as a Sina record. If `True`, uses id as filename.
        :type sina_record: bool or str
        :param output_format: Output format must either be 'json' or 'hdf5'
        :type output_format: str
        :return: dataset and its associated data
        :rtype: dict"""
        rec = self.get_record()
        relationships = self.get_sina_store().relationships.find(self.id)
        # cleanup the record
        rec_json = cleanup_sina_record_from_kosh_sync(rec)
        jsns = [rec_json, ]
        # ok now same for associated data
        for associated_id in self._associated_data_:
            if associated_id.startswith(f"{self.id}__uri__"):
                # ok self referencing no need to add
                continue
            rec = self.__store__._load(associated_id).get_record()
            rec_json = cleanup_sina_record_from_kosh_sync(rec)
            jsns.append(rec_json)

        # returns a dict that should be ingestible by sina
        output_dict = {
            "minimum_kosh_version": None,
            "kosh_version": kosh.version(comparable=True),
            "sources_type": self.__store__._sources_type,
            "records": jsns,
            "relationships": relationships
        }

        update_json_file_with_records_and_relationships(file, output_dict)

        if sina_record:
            if output_format.lower() == 'json':
                from sina.utils import save_doc_as_json
                try:
                    save_doc_as_json([rec], relationships, sina_record)
                except:  # noqae722
                    save_doc_as_json([rec], relationships, f"{rec.id}.json")
            elif output_format.lower() == 'hdf5':
                from sina.utils import save_doc_to_hdf5
                try:
                    save_doc_to_hdf5([rec], relationships, sina_record)
                except:  # noqae722
                    save_doc_to_hdf5([rec], relationships, f"{rec.id}.hdf5")
            else:
                print("output_format must either be 'json' or 'hdf5'")

        return output_dict

    @lock_strategies.lock_method
    def get_associated_data(self, ids_only=False):
        """Generator of associated data
        :param ids_only: generator will return ids if True Kosh object otherwise
        :type ids_only: bool
        :returns: generator
        :rtype: str or Kosh objects
        """
        for id in self._associated_data_:
            if ids_only:
                yield id
            else:
                yield self.__store__._load(id)

    @lock_strategies.lock_method
    def is_member_of(self, ensemble):
        """Determines if this dataset is a member of the passed ensemble
        :param ensemble: ensemble we need to determine if this dataset is part of
        :type ensemble: str or KoshEnsemble

        :returns: True if member of the ensemble, False otherwise
        :rtype: bool"""
        if not isinstance(ensemble, (six.string_types, kosh.ensemble.KoshEnsemble)):
            raise TypeError("ensemble must be id or KoshEnsemble object")
        if isinstance(ensemble, kosh.ensemble.KoshEnsemble):
            ensemble = ensemble.id

        return ensemble in self.get_ensembles(ids_only=True)

    @lock_strategies.lock_method
    def get_ensembles(self, ids_only=False):
        """Returns the ensembles this dataset is part of
        :param ids_only: return ids or objects
        :type ids_only: bool
        """
        for rel in self.get_sina_store().relationships.find(
                self.id, self.__store__._ensemble_predicate, None):
            if ids_only:
                yield rel.object_id
            else:
                yield self.__store__.open(rel.object_id, requestorId=self.id)

    @lock_strategies.lock_method
    def leave_ensemble(self, ensemble):
        """Removes this dataset from an ensemble
        :param ensemble: The ensemble to leave
        :type ensemble: str or KoshEnsemble
        """
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write'])
        from kosh.ensemble import KoshEnsemble
        if isinstance(ensemble, six.string_types):
            ensemble = self.__store__.open(ensemble)
        if not isinstance(ensemble, KoshEnsemble):
            raise ValueError(
                "cannot join `ensemble` since object `{}` does not map to an ensemble".format(ensemble))
        if self.id in ensemble.get_members(ids_only=True):
            ensemble.remove(self.id)
        else:
            warnings.warn(
                "{} is not part of ensemble {}. Ignoring request to leave it.".format(
                    self.id, ensemble.id))

    @lock_strategies.lock_method
    def join_ensemble(self, ensemble):
        """Adds this dataset to an ensemble
        :param ensemble: The ensemble to join
        :type ensemble: str or KoshEnsemble
        """
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write', 'append'])
        from kosh.ensemble import KoshEnsemble
        if isinstance(ensemble, six.string_types):
            ensemble = self.__store__.open(ensemble, requestorId=self.id)
        if not isinstance(ensemble, KoshEnsemble):
            raise ValueError(
                "cannot join `ensemble` since object `{}` does not map to an ensemble".format(ensemble))
        ensemble.add(self)

    @lock_strategies.lock_method
    def clone(self, preserve_ensembles_memberships=False, id_only=False):
        """Clones the dataset, e.g makes an identical copy.

        :param preserve_ensembles_memberships: Add the new dataset to the ensembles this original dataset belongs to?
                                               True/1:  The cloned dataset will belong to the same ensembles
                                                        as the original dataset.
                                               False/0: The new dataset will not belong to any ensemble
                                                        but we will copy ensemble level attributes onto
                                                        the cloned dataset.
                                               -1:      The new dataset will not belong to any ensemble and we
                                                        will leave out all attributes that belong to ensembles.
        :type preserve_ensembles_membership: bool or int

        :param id_only: returns id rather than new dataset
        :type id_only: bool

        :returns: The cloned dataset or its id
        :rtype: KoshDataset or str
        """
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write', 'append'])
        attributes = self.list_attributes(True)
        cloned_dataset = self.__store__.create(metadata=attributes)
        for associated in self.get_associated_data():
            rec = associated.get_record()
            if "uri" not in rec["data"]:
                continue
            cloned_dataset.associate(
                associated.uri,
                associated.mime_type,
                metadata=associated.list_attributes(True))

        if preserve_ensembles_memberships in [True, 1]:
            for ensemble in self.get_ensembles():
                ensemble.add(cloned_dataset)
        elif preserve_ensembles_memberships == -1:
            for attribute in self.list_attributes():
                if self.is_ensemble_attribute(attribute):
                    delattr(cloned_dataset, attribute)
        elif preserve_ensembles_memberships != 0:
            raise ValueError(
                "preserve_ensembles_memberships must be one of True/1, False/0 or -1")

        if id_only:
            return cloned_dataset.id
        else:
            return cloned_dataset

    @lock_strategies.lock_method
    def is_ensemble_attribute(self, attribute, ensembles=None, ensemble_id=False):
        """Determine if an attribute belongs to ensemble this dataset is part of
        :param attribute: The attribute to check
        :type attribute: str
        :param ensembles: ensembles to check against, defaults to all ensembles the dataset belongs to
        :type ensembles: None, ensemble_id or ensemble_obj or list of these
        :param ensemble_id: rather than True/False return the id of the ensemble this attribute comes from
        :type ensemble_id: bool
        :returns: True or ensemble of origin id if the attribute belongs to an ensemble False/"" otherwise
        """
        if ensembles is None:
            ensembles = self.get_ensembles()
        elif isinstance(ensembles, str):
            try:
                ensembles = self.__store__.open(ensembles, requestorId=self.id)
            except Exception:
                raise ValueError(
                    "could not find object with id {} in the store".format(ensembles))
            ensembles = [ensembles, ]
        elif not isinstance(ensembles, Iterable):
            ensembles = [ensembles, ]
        for ensemble in ensembles:
            if not isinstance(ensemble, kosh.ensemble.KoshEnsemble):
                raise ValueError(
                    "Object with id {} is not an ensemble {}".format(
                        ensemble.id, type(ensemble)))

            if attribute in ensemble.list_attributes(no_duplicate=True):
                if ensemble_id:
                    return ensemble.id
                else:
                    return True
        if ensemble_id:
            return ""
        else:
            return False

    @lock_strategies.lock_method
    def list_ensemble_tags(self, ensemble_id, dictionary=False, obscure=True):
        """list all ensemble tags of specific ensemble ids

        :param ensemble_id: Ensemble ID(s) of ensemble(s)
        :type ensemble_id: str, str
        :param dictionary: return a dictionary of value/pair rather than just tag names
        :type dictionary: bool
        :param obscure: Don't return backend attributes such as 'INHERIT_ATTRIBUTES'
        :type obscure: bool

        :return: list of ensemble tags for dataset of a specific ensemble
        :rtype: list
        """
        ens_tags = self.list_attributes(ensemble_id=ensemble_id, dictionary=dictionary, obscure=obscure)
        if dictionary:
            return {key: val for key, val in ens_tags.items() if "_ENSEMBLE_TAG_" in key}
        else:
            return [et for et in ens_tags if "_ENSEMBLE_TAG_" in et]

    @lock_strategies.lock_method
    def add_ensemble_tags(self, ensemble_id, ensemble_tags):
        """add ensemble tags to a specific ensemble

        :param ensemble_id: Ensemble ID of ensemble
        :type ensemble_id: str
        :param ensemble_tags: Ensemble tags and their values to add
        :type ensemble_tags: dict
        """
        for key, val in ensemble_tags.items():
            self.___setattr___(f"{ensemble_id}_ENSEMBLE_TAG_{key}", val, force=True)

    @lock_strategies.lock_method
    def delete_ensemble_tags(self, ensemble_id, ensemble_tags):
        """remove ensemble tags from a specific ensemble

        :param ensemble_id: Ensemble ID of ensemble
        :type ensemble_id: str
        :param ensemble_tags: Ensemble tags to remove
        :type ensemble_tags: list
        """
        if isinstance(ensemble_tags, str):
            ensemble_tags = [ensemble_tags]
        for et in ensemble_tags:
            attr = f"{ensemble_id}_ENSEMBLE_TAG_{et}"
            delattr(self, attr)

    @lock_strategies.lock_method
    def add_curve(self, curve, curve_set=None, curve_name=None, independent=None, units=None, tags=None):
        """Add a curve to a dataset
        :param curve: The curve data
        :type curve: array-like
        :param curve_set: Name of the curve_set.
                          If not passed will be set to curve_x where x is the highest number available
                          (if non exist then curve_set_0 will be created)
        :type curve_set: str
        :param curve_name: name of the curve.
                           If not set it will be set to: curve_x where x is the number of curves in this curve_set
        :type curve_name: str
        :param independent: Is it an independent variable. If not passed, it will be set to False
                            unless no independent curve exists, e.g first curve is set as independent
                            You can avoid this by explicitly passing False
        :type independent: bool
        :param units: Units of the curve (if any)
        :type units: str
        :param tags: Tags on the curve (if any)
        :type tags: dict

        :returns: the curve_set/curve_name path
        :rtype: str
        """
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write', 'append'])
        # Before anything else lets remove the cached features
        cached_features = self.__store__._cached_features_
        yank = []
        for id in cached_features:
            if id.endswith(self.id):
                yank.append(id)
        for id in yank:
            del cached_features[id]
        # put back in store
        self.__store__._cached_features_ = cached_features

        # let's obtain the record
        rec = self.get_record()
        # Let's figure out the curve_set name
        if curve_set is None:
            i = 0
            while "curve_set_"+str(i) in rec.raw["curve_sets"]:
                i += 1
            if i > 0:
                i -= 1
            curve_set = "curve_set_"+str(i)

        # Let's create curveset if not present
        if curve_set not in rec.raw["curve_sets"]:
            cs = rec.add_curve_set(curve_set)
        else:
            cs = rec.get_curve_set(curve_set)
        # Ok now let's get a curve_name
        if curve_name is None:
            i = 0
            while "curve_"+str(i) in cs.dependent or "curve_"+str(i) in cs.independent:
                i += 1
            curve_name = "curve_"+str(i)

        if curve_name in cs.independent or curve_name in cs.dependent:
            raise ValueError("curve {} already exist in curve_set {}".format(curve_name, curve_set))
        # Finally the independent part
        if independent is None:
            if len(cs.independent) == 0:
                independent = True
            else:
                independent = False
        if independent:
            cs.add_independent(curve_name, curve, units, tags)
        else:
            cs.add_dependent(curve_name, curve, units, tags)

        if self.__store__.__sync__:
            self._update_record(rec)
        else:
            self._update_record(rec, self.__store__._added_unsync_mem_store)

        # Since we changed the curves, we need to cleanup
        # the features cache
        self.__features__[None] = {}

        return "{}/{}".format(curve_set, curve_name)

    @lock_strategies.lock_method
    def remove_curve_or_curve_set(self, curve, curve_set=None):
        """Removes a curve or curve_set from the dataset
        :param curve: name of the curve or curve_set to remove
        :type curve: str
        :param curve_set: curve_set the curve_name belongs to.
                          If not passed then assumes it is in the curve
                          name.
        :type curve_set: str
        """
        __check_valid_connection_type__(self.__store__.__connection_type__, ['write'])
        original_curve_set = curve_set
        rec = self.get_record()
        if curve_set is None:
            # User did not pass the curve_set
            # The curve_set might be prepended to the curve_name then.
            try:
                curve_set, curve = kosh.utils.find_curveset_and_curve_name(curve, rec)[0]
            except Exception:
                raise ValueError("You need to pass a curve set for curve {}".format(curve))
        if curve_set not in rec.raw["curve_sets"]:
            if original_curve_set is None:
                if curve in rec.raw["curve_sets"]:
                    del rec.raw["curve_sets"][curve]
                    if self.__store__.__sync__:
                        self._update_record(rec)
                    else:
                        self._update_record(rec, self.__store__._added_unsync_mem_store)
                    self.__features__[None] = {}
                    return
            else:
                raise ValueError("The curve set {} does not exists".format(curve_set))
        cs = rec.get_curve_set(curve_set)
        if curve in cs.independent:
            del rec.raw["curve_sets"][curve_set]["independent"][curve]
        elif curve in cs.dependent:
            del rec.raw["curve_sets"][curve_set]["dependent"][curve]
        elif curve is None:
            # We want to delete the whole curveset
            del rec.raw["curve_sets"][curve_set]
        else:
            raise ValueError("Could not find {} in curve_set {}".format(curve, curve_set))
        # In case we removed everything
        if len(cs.dependent) == 0 and len(cs.independent) == 0:
            del rec.raw["curve_sets"][curve_set]

        if self.__store__.__sync__:
            self._update_record(rec)
        else:
            self._update_record(rec, self.__store__._added_unsync_mem_store)

        # Since we changed the curves, we need to cleanup
        # the features cache
        self.__features__[None] = {}
        return

    @lock_strategies.lock_method
    def list_attributes(self, dictionary=False, ensemble_id=None, obscure=True):
        """listattributes list all non protected attributes

        :param dictionary: return a dictionary of value/pair rather than just attributes names
        :type dictionary: bool
        :param ensemble_id: Provide ensemble ID(s) to return ensemble tags
        :type ensemble_id: str, lst
        :param obscure: Don't return backend attributes such as 'INHERIT_ATTRIBUTES'
        :type obscure: bool

        :return: list of attributes set on object
        :rtype: list
        """

        attributes = super(KoshDataset, self).list_attributes(dictionary=dictionary, ensemble_id=ensemble_id)
        if obscure:
            if dictionary:
                return {key: val for key, val in attributes.items() if '_ENSEMBLE_TAG_INHERIT_ATTRIBUTES' not in key}
            else:
                return [et for et in attributes if '_ENSEMBLE_TAG_INHERIT_ATTRIBUTES' not in et]
        return attributes

    @lock_strategies.lock_method
    def to_dataframe(self, data_columns=[], *atts, **keys):
        """Return the find object as a Pandas DataFrame.

        Pass in the same arguments and keyword arguments as the find method.

        find associated data matching some metadata
        arguments are the metadata name we are looking for e.g
        find("attr1", "attr2")
        you can further restrict by specifying exact value for a metadata
        via key=value
        you can return ids only by using: ids_only=True
        range can be specified via: sina.utils.DataRange(min, max)

        "file_uri" is a special key that will return the kosh object associated
        with this dataset for the given uri.  e.g store.find(file_uri=uri)

        :param data_columns: Columns to extract. By default this will include ['id', 'mime_type', 'uri', 'associated'].
                            If nothing is passed, will return all data.
        :type data_columns: Union(str, list), optional
        :return: Pandas DataFrame
        :rtype: Pandas DataFrame
        """
        import pandas as pd
        if isinstance(data_columns, str):
            data_columns = [data_columns]

        keys['load_type'] = 'dictionary'
        keys['ids_only'] = False
        sources = list(self.find(*atts, **keys))

        attr_dict = {}
        total_sources = len(sources)

        # Always have these by default
        defaults = ['id', 'mime_type', 'uri', 'associated']

        # Acquire all data if `data_columns` was not passed
        if not data_columns:
            unique_keys = []
            for i, source in enumerate(sources):
                unique_keys.extend(list(source['data'].keys()))

            data_columns = sorted(set(unique_keys))

        data_columns = defaults + data_columns  # Want defaults in front
        try:
            data_columns.remove('last_modified_date')
        except ValueError:  # if data_columns is passed this won't be there
            pass
        attr_dict = {d: [pd.NA] * total_sources for d in data_columns}

        for i, source in enumerate(sources):
            for column in data_columns:
                if column == "id":
                    attr_dict[column][i] = source['id']
                else:
                    attr_dict[column][i] = source['data'].get(column, {}).get('value', pd.NA)

        df = pd.DataFrame(attr_dict)
        return df
