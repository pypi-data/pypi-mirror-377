import os
import zeep
import requests
from zeep import Settings,AsyncClient,Client
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.helpers import serialize_object
from zeep.plugins import HistoryPlugin
import pandas as pd
import logging
from typing import Literal
from zeep.transports import AsyncTransport
import httpx
import asyncio
from datetime import datetime
from lxml import etree
from sibr_api import ApiBase,NotFoundError,RateLimitError,SkipItemException
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor



class CustomAsyncTransport(AsyncTransport):
    def __init__(self, client=None, wsdl_client=None, cache=None, timeout=300, operation_timeout=300, verify_ssl=True,proxies=None):
        #super().__init__()
        self._close_session = bool(client is None)
        self.cache = cache
        self.wsdl_client = wsdl_client or httpx.Client(
            verify=verify_ssl,
            timeout=timeout,
        )
        self.client = client or httpx.AsyncClient(
            verify=verify_ssl,
            timeout=operation_timeout,
        )
        self.logger = logging.getLogger(__name__)

class kartverketsAPI:
    def __init__(self, logger = None):
        if logger is None:
            logger = logging.getLogger("Kartverkets-api")
            logger.setLevel("INFO")
        self.logger = logger
        self.username = os.getenv("GRUNNBOK_USERNAME")
        self.password = os.getenv("GRUNNBOK_PASSWORD")

        self.settings = Settings(strict=False, xml_huge_tree=True)
        self.transport = None
        self.session = None

        self.httpx_client = None
        self.async_transport = None
        self.timeout_seconds = 60

        self.base_url = "https://www.grunnbok.no/grunnbok/wsapi/v2/"
        self.services = {
            "GrunnboksutskriftService": f"{self.base_url}GrunnboksutskriftServiceWS?WSDL",
            "RegisterenhetService": f"{self.base_url}RegisterenhetServiceWS?WSDL",
            "RettsstiftelseService": f"{self.base_url}RettsstiftelseServiceWS?WSDL",
            "InformasjonService": f"{self.base_url}InformasjonServiceWS?WSDL",
            "EndringsloggService": f"{self.base_url}EndringsloggServiceWS?WSDL",
            "NedlastningService": f"{self.base_url}NedlastningServiceWS?WSDL",
            "KodelisteService": f"{self.base_url}KodelisteServiceWS?WSDL",
            "IdentService": f"{self.base_url}IdentServiceWS?WSDL",
            "KommuneService": f"{self.base_url}KommuneServiceWS?WSDL",
            "PersonService": f"{self.base_url}PersonServiceWS?WSDL",

            # Tjenester for innsending og validering
            "InnsendingService": f"{self.base_url}InnsendingServiceWS?WSDL",
            "ValideringService": f"{self.base_url}ValideringServiceWS?WSDL",

            # Andre spesialiserte tjenester
            "StoreService": f"{self.base_url}StoreServiceWS?WSDL",
            "RettsstiftelsestypebegrensningService": f"{self.base_url}RettsstiftelsestypebegrensningServiceWS?WSDL",
            "RegisterenhetsrettsandelService": f"{self.base_url}RegisterenhetsrettsandelServiceWS?WSDL",
            "RegisterenhetsrettService": f"{self.base_url}RegisterenhetsrettServiceWS?WSDL",
            "SeksjonssameieandelService": f"{self.base_url}SeksjonssameieandelServiceWS?WSDL",
            "OverfoeringService": f"{self.base_url}OverfoeringServiceWS?WSDL",
            "RegistreringsstatusService": f"{self.base_url}RegistreringsstatusServiceWS?WSDL",
            "ForeloepigRegistreringService": f"{self.base_url}ForeloepigRegistreringServiceWS?WSDL"
        }
        self.context = self._create_context()

    def _create_context(self):
        ident_service_wsdl = self.services['IdentService']
        with requests.Session() as session:
            session.auth = HTTPBasicAuth(self.username, self.password)
            transport = Transport(session=session)
            ident_client = Client(wsdl=ident_service_wsdl, transport=transport)
            GrunnbokContext = ident_client.get_type('ns1:GrunnbokContext')
            Timestamp = ident_client.get_type('ns1:Timestamp')
            return GrunnbokContext(
                clientIdentification="sibr-python-test",
                systemVersion="v2",
                snapshotVersion=Timestamp('9999-01-01T00:00:00+01:00'),
                locale="nb_NO"
            )

    async def close(self):
        if self.httpx_client and not self.httpx_client.is_closed:
            await self.httpx_client.aclose()
            self.logger.info("Asynkron sesjon er lukket.")

    def close_sync(self):
        """En synkron wrapper for close."""
        # Unngå feil hvis løkken allerede er lukket
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # Hvis vi er inne i en annen løkke, kan vi ikke bruke asyncio.run()
                # Dette er en mer avansert problemstilling, men for enkel bruk fungerer asyncio.run()
                pass
        except RuntimeError:  # No running loop
            asyncio.run(self.close())

    async def _init_async_transport(self):
        if self.httpx_client is None:
            auth = httpx.BasicAuth(self.username, self.password)
            self.httpx_client = httpx.AsyncClient(auth=auth,timeout=self.timeout_seconds)
            # Vi sender vår egen klient inn til AsyncTransport
            # self.async_transport = AsyncTransport(client=self.httpx_client, cache=None)
            self.async_transport = CustomAsyncTransport(self.httpx_client)
            self.logger.info("Async transport initiated")

    def _init_transport(self):
        if self.session is None and self.transport is None:
            self.session = Session()
            self.session.auth = HTTPBasicAuth(self.username, self.password)
            self.transport = Transport(session=self.session)

    def _encode_address(self, address):

        if "/" in address:
            f = address.split("/")[0]
            l = address.split("/")[1].split(",")
            address = f"{f}, {''.join(l[1:])}"

        try:
            encoded_address = quote_plus(address)


            if not isinstance(encoded_address, str) or not encoded_address.strip():
                self.logger.warning(
                    f"Skipping address: {address}. No valid output after encoding: {encoded_address}")
                return None
        except Exception as e:
            encoded_address = address
            self.logger(f'Could not encode address {address} | {e}')

        return encoded_address

    def _get_prefix_for_uri(self, client, target_uri):
        for prefix, uri in client.namespaces.items():
            if uri == target_uri:
                return prefix
        raise ValueError(f"Ingen prefix funnet for URI: {target_uri}. Sjekk namespaces-print.")

    def _ensure_col_names(self, col_names: list[str]):
        new_col_names = []
        for col_name in col_names:
            new_col_names.append(
                col_name.strip().lower().replace(' ', '_').replace('-', '_').replace(".", "_").replace("ø",
                                                                                                       "o").replace("æ",
                                                                                                                    "a").replace(
                    "å", "a"))
        return new_col_names

    def _get_propertyIds(self, properties: list[dict],ownership_type : Literal["eier","andel"] = "eier") -> list[tuple]:
        """

        :param properties: properties will have to be in format of dictionaries with keys in
        ['kommunenummer', 'gaardsnummer', 'bruksnummer', 'festenummer', 'seksjonsnummer']
        :return: a unique property id 'RegisterenhetId' from kartverket

        example_input:
        property = {
                    "kommunenummer" : "3212",
                    "gaardsnummer" : 1,
                    "bruksnummer" : 5,
                    "festenummer": 0,
                    "seksjonsnummer": 0
                    }
        """
        starttime = datetime.now()
        self._init_transport()
        ident_service_wsdl = self.services.get('IdentService')
        ident_client = zeep.Client(wsdl=ident_service_wsdl, transport=self.transport, settings=self.settings)
        ident_client.plugins = [HistoryPlugin()]

        factory = ident_client.type_factory('ns16')
        idents = {'item': []}
        for prop in properties:
            if ownership_type == "eier":
                prop_ident = factory.MatrikkelenhetIdent(**prop)
            elif ownership_type == "andel":
                prop_ident = factory.BorettslagsandelIdent(**prop)
            else:
                raise TypeError(f'Expected "eier" or "andel", but got {ownership_type}')
            idents['item'].append(prop_ident)

        try:
            id_map = ident_client.service.findRegisterenhetIdsForIdents(
                grunnbokContext=self.context,
                idents=idents
            )
            #print(id_map)
            internal_ids = [(dict(id_entry.get("key")), id_entry.get("value").get("value")) for id_entry in serialize_object(id_map) if id_entry.get("value") is not None]
            self.logger.info(f"🔢  Fetched {len(internal_ids)} id's from {len(properties)} properties in {datetime.now() - starttime}")
            return internal_ids
        except zeep.exceptions.Fault as e:
            self.logger.error(f"SOAP-feil: {e.message} when passing properties. Example from property inputs: {properties[:3]}")
            sent_xml_obj = ident_client.plugins[0].last_sent['envelope']
            sent_xml_str = etree.tostring(sent_xml_obj, pretty_print=True).decode('utf-8')
            self.logger.error(f"Sent XML:\n{sent_xml_str}")
            return []
        except Exception as e:
            self.logger.error(f"Error when fetching property ids: {str(e)} | properties example: {properties[:3]}")
            return []

    async def _get_propertyIds_async(self, properties: list[dict], ownership_type: Literal["eier", "andel"] = "eier",
                                     batch_size: int = 500) -> list[tuple]:
        """
        Henter RegisterenhetId asynkront ved å sende properties i parallelle batches.
        """
        starttime = datetime.now()
        await self._init_async_transport()
        ident_service_wsdl = self.services.get('IdentService')
        ident_client = AsyncClient(wsdl=ident_service_wsdl, transport=self.async_transport, settings=self.settings)
        ident_client.plugins = [HistoryPlugin()]
        self.logger.info(f"✅ Async connection to IdentService is ready. url {ident_service_wsdl}")

        # Del opp properties i mindre lister (batches)
        property_batches = [properties[i:i + batch_size] for i in range(0, len(properties), batch_size)]

        # Begrens antall samtidige kall mot API-et
        semaphore = asyncio.Semaphore(10)

        # Indre "worker"-funksjon som håndterer ett enkelt batch-kall
        async def fetch_batch(batch_props: list[dict]):
            async with semaphore:
                if not batch_props:
                    return []  # Hopp over tomme lister

                factory = ident_client.type_factory('ns16')
                idents = {'item': []}
                for prop in batch_props:
                    if ownership_type == "eier":
                        prop_ident = factory.MatrikkelenhetIdent(**prop)
                    elif ownership_type == "andel":
                        prop_ident = factory.BorettslagsandelIdent(**prop)
                    else:  # Denne sjekken trengs egentlig bare én gang, men er trygg å ha her
                        self.logger.error(
                            f'Invalid ownership_type: Expected "eier" or "andel", but got {ownership_type}')
                        return []
                    idents['item'].append(prop_ident)

                try:
                    id_map = await ident_client.service.findRegisterenhetIdsForIdents(
                        grunnbokContext=self.context,
                        idents=idents
                    )

                    # Behandle resultatet for denne batchen
                    internal_ids = [(dict(id_entry.get("key")), id_entry.get("value").get("value"))
                                    for id_entry in serialize_object(id_map)
                                    if id_entry.get("value") is not None]
                    return internal_ids

                except zeep.exceptions.Fault as e:
                    self.logger.error(f"SOAP-error in batch: {e.message}. Example from batch: {batch_props[:2]}")
                    sent_xml_obj = ident_client.plugins[0].last_sent['envelope']
                    sent_xml_str = etree.tostring(sent_xml_obj, pretty_print=True).decode('utf-8')
                    self.logger.error(f"Sent XML for failed batch:\n{sent_xml_str}")
                    return []  # Returner tom liste for denne batchen ved feil
                except Exception as e:
                    self.logger.error(f"Error in batch: {str(e)} | Example from batch: {batch_props[:2]}")
                    return []

        # Opprett en task for hver batch
        tasks = [fetch_batch(batch) for batch in property_batches]

        all_ids = []

        # Kjør tasks og samle resultater etter hvert som de blir ferdige
        for i, future in enumerate(asyncio.as_completed(tasks)):
            self.logger.debug(f"\tProcessing property batch {i + 1}/{len(tasks)}...")
            ids_from_batch = await future
            if ids_from_batch:
                all_ids.extend(ids_from_batch)

        self.logger.info(
            f"🔢 Fetched {len(all_ids)} id's from {len(properties)} properties in {datetime.now() - starttime}")
        return all_ids

    async def _get_single_transId_by_propertyId(self, client, id,transfer_type : Literal["active","historical"] = "active"):
        #try:
        if transfer_type == "active":
            overdragelser_map = await client.service.findOverdragelserMedAktiveAndelerIRegisterenhet(
                grunnbokContext=self.context,
                registerenhetId=id
            )
            return overdragelser_map
        elif transfer_type == "historical":
            overdragelser_map = await client.service.findOverdragelserMedHistoriskeAndelerIRegisterenhet(
                grunnbokContext=self.context,
                registerenhetId=id
            )
            return overdragelser_map
        # except Exception as e:
        #     self.logger.error(f"Error fetching {id}: {str(e)}")
        #     #raise

    async def _get_transferIds_by_propertyIds(self, ids: list[str], transfer_type : Literal["active","historical"] = "active",):
        start = datetime.now()
        await self._init_async_transport()
        rettsstiftelse_wsdl = self.services.get("RettsstiftelseService")
        rettsstiftelse_client = AsyncClient(wsdl=rettsstiftelse_wsdl, transport=self.async_transport,
                                            settings=self.settings)
        rettsstiftelse_client.plugins = [HistoryPlugin()]
        self.logger.info(f"✅ Connection to Api url is ready. url {rettsstiftelse_wsdl}")

        reg_uri = 'http://kartverket.no/grunnbok/wsapi/v2/domain/register/registerenhet'
        reg_prefix = self._get_prefix_for_uri(rettsstiftelse_client, reg_uri)
        reg_factory = rettsstiftelse_client.type_factory(reg_prefix)

        try:

            registerenhet_ids = [reg_factory.RegisterenhetId(value=id_str) for id_str in ids]

            semaphore = asyncio.Semaphore(20)

            async def exe_async(reg_id):
                async with semaphore:
                    try:
                        id_str = serialize_object(reg_id).get("value")
                        result = await self._get_single_transId_by_propertyId(rettsstiftelse_client, reg_id, transfer_type)
                        #print(f'id: {id_str} result: {result}')
                        return (id_str, result)
                    except zeep.exceptions.Fault as e:
                        self.logger.error(f"SOAP-feil: {e.message}")
                        # Hent ut 'envelope'-objektet og konverter det til en lesbar streng
                        sent_xml_obj = rettsstiftelse_client.plugins[0].last_sent['envelope']
                        sent_xml_str = etree.tostring(sent_xml_obj, pretty_print=True).decode('utf-8')
                        self.logger.error(f"Sent XML:\n{sent_xml_str}")  # <--- FIKSEN
                        return (id_str, None)
                    except ValueError as e:
                        self.logger.error(f"ValueError fetching {id_str}: {str(e)}")
                        raise
                    except Exception as e:
                        self.logger.error(f"Error fetching {id_str}: {str(e)}. Returning {(id_str, None)}")
                        return (id_str, None)

            tasks = [exe_async(reg_id = reg_id) for reg_id in registerenhet_ids]

            results_map = {}
            for i,future in enumerate(asyncio.as_completed(tasks)):
                id_str, output = await future
                #print(f'id: {id_str} Output: {output}')
                if i % 5000 == 0:
                    self.logger.info(f'\tProcessing the {i}th item, id: {id_str}')
                if output:
                    #print(f'Type {type(output)}')
                    #print(f'Type element {type(output[0])}')
                    overdragelse_ids = [serialize_object(item).get("value").get("value") for item in output if item and serialize_object(item).get("value")]
                    andel_ids = [serialize_object(item).get("key").get("value") for item in output if item and serialize_object(item).get("key")]
                    results_map[id_str] = {"overdragelse_ids": overdragelse_ids, "andel_ids": andel_ids}
                else:
                    results_map[id_str] = {"overdragelse_ids": [], "andel_ids": []}
            self.logger.info(f'🔗  Fetched transfer ids from {len(ids)} ids in {datetime.now()-start}')
            return results_map
        except zeep.exceptions.Fault as e:
            self.logger.error(f"SOAP-feil: {e.message}")
            # Hent ut 'envelope'-objektet og konverter det til en lesbar streng
            sent_xml_obj = rettsstiftelse_client.plugins[0].last_sent['envelope']
            sent_xml_str = etree.tostring(sent_xml_obj, pretty_print=True).decode('utf-8')
            self.logger.error(f"Sent XML:\n{sent_xml_str}")  # <--- FIKSEN
            return (id_str, None)
        except ValueError as ve:
            self.logger.error(f"Namespace-feil: {ve}")
            raise
        except Exception as e:
            self.logger.error(f"Annen feil: {str(e)}")
            return {}

    def _get_transferIds_by_period(self, fra_dato: str, til_dato: str, rettstype_koder: list[int] = [18]):
        # if self.session is None or self.transport is None:
        start = datetime.now()
        self._init_transport()
        rettsstiftelse_wsdl = self.services.get('RettsstiftelseService')
        rettsstiftelse_client = zeep.Client(wsdl=rettsstiftelse_wsdl, transport=self.transport, settings=self.settings)
        self.logger.info(f"✅ Tilkobling til Api url er klar. url {rettsstiftelse_wsdl}")

        bas_factory = rettsstiftelse_client.type_factory('ns1')  # basistyper
        kod_factory = rettsstiftelse_client.type_factory('ns3')  # koder
        timestamp_type = bas_factory.Timestamp
        kode_ids = {'item': [kod_factory.RettstypeKodeId(value=kode) for kode in rettstype_koder]}

        overdragelse_ids = rettsstiftelse_client.service.findOverdragelserForPeriode(
            grunnbokContext=self.context,
            rettstypeKodeIds=kode_ids,
            fraOgMedDato=timestamp_type(fra_dato + 'T00:00:00+01:00'),
            tilOgMedDato=timestamp_type(til_dato + 'T00:00:00+01:00')
        )
        obj = serialize_object(overdragelse_ids)
        self.logger.info(f"📅  Fetched {len(obj)} objects for period {fra_dato} - {til_dato} with rettstype_koder {rettstype_koder} in {datetime.now()-start}")
        return [o.get("value") for o in obj]

    def _get_info_by_transferIds(self, overdragelse_ids: list[str]):
        # if self.session is None or self.transport is None:
        start = datetime.now()
        self._init_transport()
        store_wsdl = self.services.get('StoreService')
        store_client = zeep.Client(wsdl=store_wsdl, transport=self.transport, settings=self.settings)
        self.logger.info(f"✅ Connection to Api url is ready. url {store_wsdl}")
        ret_factory = store_client.type_factory('http://kartverket.no/grunnbok/wsapi/v2/domain/register/rettsstiftelse')
        store_ids = {
            'item': [ret_factory.RettsstiftelseId(value=oid) for oid in overdragelse_ids if oid]
        }

        try:
            objects = store_client.service.getObjects(
                grunnbokContext=self.context,
                ids=store_ids
            )
            self.logger.info(f"ℹ️  Fetched {len(objects)} info objects from {len(overdragelse_ids)} transfer ids in {datetime.now() - start}")
            return objects
        except zeep.exceptions.Fault as e:
            self.logger.error(f"SOAP-error in getObjects: {e.message}")
            self.logger.error(
                f"Sent XML:\n {store_client.plugins[0].last_sent if store_client.plugins else 'No history'}")
            return []
        except Exception as e:
            self.logger.error(f"Other error in getObjects: {str(e)}")
            return []

    async def _get_info_by_transferIds_async(self, overdragelse_ids: list[str], batch_size: int = 100):
        """
        Henter info-objekter asynkront ved å dele opp ID-er i batches og kjøre dem parallelt.
        """
        start = datetime.now()
        # Bruk den asynkrone initialiseringen
        await self._init_async_transport()
        store_wsdl = self.services.get('StoreService')
        # Bruk AsyncClient for asynkrone kall
        store_client = AsyncClient(wsdl=store_wsdl, transport=self.async_transport, settings=self.settings)
        store_client.plugins = [HistoryPlugin()]  # For bedre feilsøking
        self.logger.info(f"✅ Async connection to Api url is ready. url {store_wsdl}")

        # Forbered type factory for å bygge SOAP-objekter
        ret_factory = store_client.type_factory('http://kartverket.no/grunnbok/wsapi/v2/domain/register/rettsstiftelse')

        # Del opp den store listen i mindre batches
        id_batches = [overdragelse_ids[i:i + batch_size] for i in range(0, len(overdragelse_ids), batch_size)]

        # Begrens antall samtidige kall for å ikke overbelaste API-et
        semaphore = asyncio.Semaphore(10)

        # Indre funksjon som håndterer ett enkelt batch-kall
        async def fetch_batch(batch_ids: list[str]):
            async with semaphore:
                # Bygg SOAP-objektet for denne batchen
                store_ids = {
                    'item': [ret_factory.RettsstiftelseId(value=oid) for oid in batch_ids if oid]
                }

                if not store_ids['item']:
                    return []  # Ikke gjør kall for tomme lister

                try:
                    # Kjør selve API-kallet asynkront
                    objects = await store_client.service.getObjects(
                        grunnbokContext=self.context,
                        ids=store_ids
                    )
                    return objects
                except zeep.exceptions.Fault as e:
                    self.logger.error(f"SOAP-error in batch getObjects: {e.message}")
                    # Logg XML-en som ble sendt for enklere feilsøking
                    if store_client.plugins:
                        sent_xml_obj = store_client.plugins[0].last_sent['envelope']
                        sent_xml_str = etree.tostring(sent_xml_obj, pretty_print=True).decode('utf-8')
                        self.logger.error(f"Sent XML for failed batch:\n{sent_xml_str}")
                    return []  # Returner tom liste for denne batchen ved feil
                except Exception as e:
                    self.logger.error(f"Other error in batch getObjects: {str(e)}")
                    return []

        # Opprett en task for hver batch
        tasks = [fetch_batch(batch) for batch in id_batches]

        all_objects = []

        # Kjør tasks og samle resultater
        for i, future in enumerate(asyncio.as_completed(tasks)):
            self.logger.debug(f"\tProcessing batch {i + 1}/{len(tasks)}...")
            objects_from_batch = await future
            if objects_from_batch:
                # Bruk extend for å "flate ut" listene med resultater
                all_objects.extend(objects_from_batch)

        self.logger.info(
            f"ℹ️  Fetched {len(all_objects)} info objects from {len(overdragelse_ids)} transfer ids in {datetime.now() - start}")
        return all_objects

    def _get_info_by_docId(self, doc_ids: list) -> dict:
        start = datetime.now()
        store_wsdl = self.services.get('StoreService')
        store_client = zeep.Client(wsdl=store_wsdl, transport=self.transport, settings=self.settings)
        doc_factory = store_client.type_factory('http://kartverket.no/grunnbok/wsapi/v2/domain/register/dokument')

        store_ids = {
            'item': [doc_factory.DokumentId(value=doc_id) for doc_id in doc_ids],
        }
        doc_objects = store_client.service.getObjects(
            grunnbokContext=self.context,
            ids=store_ids)

        document_map = {serialize_object(doc).get("id").get("value") : doc for doc in doc_objects if doc and serialize_object(doc).get("id")}
        transfer_date = {}
        for key, val in document_map.items():
            val = serialize_object(val)
            transfer_date[key] = val.get("registreringstidspunkt").get("timestamp")
        self.logger.info(f'📅  Fetched {len(transfer_date)} transfer dates from {len(doc_ids)} transfer ids in {datetime.now() - start}')
        return transfer_date

    async def _get_info_by_docId_async(self, doc_ids: list, batch_size: int = 100) -> dict:
        """
        Henter dokumentinfo (spesifikt 'registreringstidspunkt') asynkront
        ved å sende dokument-IDer i parallelle batches.
        """
        start = datetime.now()
        await self._init_async_transport()
        store_wsdl = self.services.get('StoreService')
        store_client = AsyncClient(wsdl=store_wsdl, transport=self.async_transport, settings=self.settings)
        store_client.plugins = [HistoryPlugin()]
        self.logger.info(f"✅ Async connection to StoreService is ready. url {store_wsdl}")

        # Del opp den store listen i mindre batches
        doc_id_batches = [doc_ids[i:i + batch_size] for i in range(0, len(doc_ids), batch_size)]

        # Begrens antall samtidige kall mot API-et
        semaphore = asyncio.Semaphore(10)

        # Indre "worker"-funksjon som håndterer ett enkelt batch-kall
        async def fetch_batch(batch_doc_ids: list):
            async with semaphore:
                if not batch_doc_ids:
                    return {}  # Hopp over tomme lister

                doc_factory = store_client.type_factory(
                    'http://kartverket.no/grunnbok/wsapi/v2/domain/register/dokument')
                store_ids = {
                    'item': [doc_factory.DokumentId(value=doc_id) for doc_id in batch_doc_ids],
                }

                try:
                    # Kjør selve API-kallet asynkront
                    doc_objects = await store_client.service.getObjects(
                        grunnbokContext=self.context,
                        ids=store_ids)

                    # Behandle resultatet for denne batchen
                    document_map = {serialize_object(doc).get("id").get("value"): doc for doc in doc_objects if
                                    doc and serialize_object(doc).get("id")}
                    transfer_date_batch = {}
                    for key, val in document_map.items():
                        val = serialize_object(val)
                        transfer_date_batch[key] = val.get("registreringstidspunkt").get("timestamp")

                    return transfer_date_batch

                except zeep.exceptions.Fault as e:
                    self.logger.error(f"SOAP-error in batch getObjects by docId: {e.message}")
                    if store_client.plugins:
                        sent_xml_obj = store_client.plugins[0].last_sent['envelope']
                        sent_xml_str = etree.tostring(sent_xml_obj, pretty_print=True).decode('utf-8')
                        self.logger.error(f"Sent XML for failed batch:\n{sent_xml_str}")
                    return {}  # Returner en tom dict for denne batchen ved feil
                except Exception as e:
                    self.logger.error(f"Other error in batch getObjects by docId: {str(e)}")
                    return {}

        # Opprett en task for hver batch
        tasks = [fetch_batch(batch) for batch in doc_id_batches]

        final_transfer_dates = {}

        # Kjør tasks og slå sammen resultat-dictionaries
        for i, future in enumerate(asyncio.as_completed(tasks)):
            self.logger.debug(f"\tProcessing document batch {i + 1}/{len(tasks)}...")
            batch_result_dict = await future
            if batch_result_dict:
                final_transfer_dates.update(batch_result_dict)

        self.logger.info(
            f'📅  Fetched {len(final_transfer_dates)} transfer dates from {len(doc_ids)} document ids in {datetime.now() - start}')
        return final_transfer_dates

    def _iaobject_to_dataframe(self, objects: list[dict],property_map = None) -> pd.DataFrame:
        """
        A function to create output as a dataframe.

        Args:
            objects (list[dict]): The list of objects to convert.
            property_map (dict): Optional. A map of property ids to transfer ids (id_value is transfer_id)

        Example:
            property_map = {'3609928': {'overdragelse_ids': ['141662867', '141662867'],
                                          'andel_ids': ['121963093', '121963094']},
                             '1414777': {'overdragelse_ids': ['130621092'], 'andel_ids': ['110439107']},
                             '806212466': {'overdragelse_ids': [], 'andel_ids': []}}
        """
        start = datetime.now()
        df = pd.json_normalize(serialize_object(objects))
        df.columns = self._ensure_col_names(df.columns)
        if property_map:
            count = 0
            for prop, ids in property_map.items():
                if count % 5000 == 0:
                    self.logger.debug(f"Matched {count} objects. ID no.: {ids}")
                count += 1
                for id in ids.get("overdragelse_ids"):
                    df.loc[df["id_value"] == id, "property_id"] = prop
        self.logger.info(f"📊  Transformed {len(objects)} object to dataframe with shape: {df.shape} in {datetime.now() - start}")
        return df

    def _object_to_dataframe(self, objects: list[dict], property_map=None) -> pd.DataFrame:
        """
        A function to create output as a dataframe. Optimized for performance.
        """
        start = datetime.now()
        df = pd.json_normalize(serialize_object(objects))
        df.columns = self._ensure_col_names(df.columns)

        if property_map:
            transfer_to_property_map = {
                transfer_id: prop_id
                for prop_id, ids in property_map.items()
                for transfer_id in ids.get("overdragelse_ids", [])
            }

            df['property_id'] = df['id_value'].map(transfer_to_property_map)

        self.logger.info(
            f"📊  Transformed {len(objects)} object to dataframe with shape: {df.shape} in {datetime.now() - start}")
        return df

    async def get_by_property(self, properties: list[dict], transfer_type : Literal["active","historical"] = "active",ownership_type : Literal["eier","andel"] = "eier"):
        starttime = datetime.now()
        # GET PROPERTY IDS
        self.logger.info(
            f'🔢  Fetching property ids for {len(properties)} properties with ownership type {ownership_type}')
        ids = await  self._get_propertyIds_async(properties, ownership_type=ownership_type)
        prop_dict = {}
        for id_tuple in ids:
            prop, id_val = id_tuple
            prop_dict[id_val] = prop
        props_df = pd.DataFrame.from_dict(prop_dict, orient='index').reset_index().rename(
            columns={"index": "property_id"})

        # GET TRANSFER IDS
        self.logger.info(f'🔗  Fetching transfer ids for {len(ids)} properties with transfer type {transfer_type}')
        trans_id_prop = await self._get_transferIds_by_propertyIds(ids=list(prop_dict.keys()),
                                                                   transfer_type=transfer_type)
        overdragelse_ids = []
        for _, val in trans_id_prop.items():
            val.get("overdragelse_ids")
            overdragelse_ids.extend(val.get("overdragelse_ids"))
        if not overdragelse_ids:
            self.logger.warning(f'No transactions found for {len(properties)} with ownership type {ownership_type} and transfer_type {transfer_type}')
            return None

        # GET INFO FROM EACH TRANSFER ID
        self.logger.info(f'ℹ️  Fetching info for {len(overdragelse_ids)} transfers')
        objects = await self._get_info_by_transferIds_async(overdragelse_ids)
        if not objects:
            self.logger.warning(f'No info found for {len(properties)} properties with ownership type {ownership_type} and transfer_type {transfer_type}')
            return None

        # GET INFO BY DOCID
        doc_ids = []
        for e in serialize_object(objects):
            doc_ids.append(e.get("dokumentId").get("value"))
        self.logger.info(f'📅  Fetching tranfer dates for {len(doc_ids)} transfers')
        transfer_date = await self._get_info_by_docId_async(doc_ids)
        if not transfer_date:
            self.logger.warning(f'No transfer dates found for {len(properties)} properties with ownership type {ownership_type} and transfer_type {transfer_type} ')
            return None

        # MAKE OUTOUT
        self.logger.info(f'📊  Transforming the output')
        df_raw = self._object_to_dataframe(objects=objects, property_map=trans_id_prop)
        if df_raw.empty:
            self.logger.warning(f'No output after making dataframe for {len(properties)} properties with ownership type {ownership_type} and transfer_type {transfer_type}')
            return None
        if "property_id" in df_raw.columns and "property_id" in props_df.columns:
            df = pd.merge(df_raw, props_df, on="property_id", how="left")
        else:
            raise ValueError(f'property_id missing in one of the dataframes')
        if df.empty:
            self.logger.warning(f'No output after merging dataframes for {len(properties)} properties with ownership type {ownership_type} and transfer_type {transfer_type}')
            return None

        if "dokumentid_value" in df.columns:
            df["registreringstidspunkt"] = df["dokumentid_value"].map(transfer_date)
            df["registreringstidspunkt"] = pd.to_datetime(df["registreringstidspunkt"], utc=True)
        else:
            raise ValueError(f'dokumentid_value not in dataframe')
        self.logger.info(
            f'Getting {len(df)} successful results from {len(properties)} in total time: {datetime.now() - starttime}.')
        return df

    def get_by_period(self, start_date: str, end_date: str, property_types: list = [18, 116],):
        #GET TRANSFER IDS
        ids = self._get_transferIds_by_period(start_date, end_date, property_types)

        #GET INFO BY TRANSFER IDS
        objects = self._get_info_by_transferIds(ids)

        # GET INFO BY DOCID
        doc_ids = []
        for e in serialize_object(objects):
            doc_ids.append(e.get("dokumentId").get("value"))
        transfer_date = self._get_info_by_docId(doc_ids)

        #MAKE OUTPUT
        df = self._object_to_dataframe(objects)
        if "dokumentid_value" in df.columns:
            df["registreringstidspunkt"] = df["dokumentid_value"].map(transfer_date)
        else:
            raise ValueError(f'dokumentid_value not in dataframe')
        return df

    def search_address(self,address = None,
                       lat = None,lon = None,radius = None,
                       search_type : Literal["address","coordinates"] = "address"):
        base_url = "https://ws.geonorge.no/adresser/v1/"
        if search_type == "address":
            search_endpoint = "sok"
            encoded_address = address
            url = f"{base_url}{search_endpoint}?sok={encoded_address}"
        elif search_type == "coordinates":
            search_endpoint = "punktsok"
            url = f"{base_url}{search_endpoint}?lat={lat}&lon={lon}&radius={radius}"
        else:
            raise TypeError(f'Expected "address" or "coordinates", but got {search_type}')
        
        headers = None

        try:
            response = requests.get(url, headers=headers)
            if response:
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        return result
                    if isinstance(result, list):
                        if len(result) == 1:
                            return result[0]
                        elif len(result) > 1:
                            self.logger.warning(f'Multiple results for address {address}')
                            return result
                        else:
                            self.logger.warning(f'No results for address {address}')
                            return None
                    elif result is None:
                        self.logger.warning(f'No results for address {address}')
                        return None
                elif response.status_code == 404:
                    self.logger.error(f'404 - Not found')
                    return None
            else:
                self.logger.error(f'API returned None')
                return None

        except Exception as e:
            self.logger.error(f'Error getting address {address}: {e}')

    def transform_single_geonorge(self,response : dict) -> list[dict] | None:
        if isinstance(response, dict):
            json_data = response
        else:
            raise TypeError(f'Not valid response type. Expected dict, but got {type(response)}')

        if json_data:
            addresses = json_data.get("adresser", [])
            metadata = json_data.get("metadata", {})

            all_data = []
            for addr in addresses:
                geo = addr.get("representasjonspunkt")
                merged_data = {**addr, **metadata, **geo}
                all_data.append(merged_data)

            df = pd.DataFrame(all_data)
            if not df.empty:
                df.columns = self._ensure_col_names(df.columns)
                to_drop = df.columns.difference(["kommunenummer", "gardsnummer", "bruksnummer", "festenummer"])
                df = df.drop(columns=to_drop)
                df.rename(columns = {"gardsnummer" : "gaardsnummer"},inplace=True)
                return df.to_dict(orient="records")
            else:
                return None
        else:
            return None

    def decode_address(self,address : str, ) -> list:
        raw_output_address = None
        clean_address = None

        try:
            self.logger.debug(f'Searching for address {address} with geonorge')
            raw_output_address = self.search_address(address=quote_plus(address))
        except Exception as e:
            self.logger.error(f'Error getting address {address}: {e}')

        if raw_output_address:
            self.logger.debug(f'Found address. Cleaning address {address} with cleaning func')
            clean_address = self.transform_single_geonorge(raw_output_address)
            if clean_address:
                return clean_address

        if clean_address is None:
            self.logger.debug(f'No hit from address search. Trying coordinates search')
            base_url = "https://nominatim.openstreetmap.org/"
            search_endpoint = "search"

            url = base_url + search_endpoint + f"?q={quote_plus(address)}&format=jsonv2"
            headers = {'User-Agent': 'YourApp/1.0'}
            response = requests.get(url, headers=headers)
            if response and response.status_code == 200:
                self.logger.debug(f'Found coordinates from address with nomimatim')
                result = response.json()
                if result and len(result)>1:
                    if isinstance(result,list):
                        lat, lon = result[0].get("lat"), result[0].get("lon")
                    elif isinstance(result,dict):
                        lat, lon = result.get("lat"), result.get("lon")
                    else:
                        raise TypeError(f'Expected list or dict, but got {type(result)}')
                    raw_output_coor = self.search_address(lat, lon, radius=100, search_type="coordinates")
                    if raw_output_coor:
                        return self.transform_single_geonorge(raw_output_coor[0])
                else:
                    self.logger.debug(f'No result from Nominatim geocode!')
            else:
                self.logger.debug(f'No result from Nominatim geocode!')
        else:
            self.logger.debug(f'no hit from either address nor coordinates search for address {address}')

    async def get_transactions(self, address : str, transfer_type : Literal["active","historical","all"],ownership_type : Literal["eier","andel"] ,section_num : int = None,coop_unit_num : int =None, coop_org_num : int = None):
        if ownership_type == "eier":
            request_cols = ["kommunenummer", "gaardsnummer", "bruksnummer", "festenummer", "seksjonsnummer"]
            if not section_num:
                self.logger.warning(f'If no "seksjonsnummer" is provided, it will be set to 0!')
        elif ownership_type == "andel":
            request_cols = ["borettslagnummer", "andelsnummer"]
            if not coop_unit_num or not coop_org_num:
                raise TypeError(f'"Andelsnummer" and "borettslagnummer" must be provided for andel ownership')
        else:
            raise ValueError(f'Expected "eier" or "andel" for ownership_type, but got {ownership_type}')

        result = self.decode_address(address)
        if not result:
            return None

        db = pd.DataFrame(result)
        if section_num:
            db["seksjonsnummer"] = section_num
        if coop_unit_num:
            db["andelsnummer"] = coop_unit_num
        if coop_org_num:
            db["borettslagnummer"] = coop_org_num


        db = self.transform_cadastrals(db, request_cols) if ownership_type == "eier" else self.transform_coop(db,request_cols)
        properties = db.to_dict(orient="records")

        transfer_type_args = ["active","historical",] if transfer_type == "all" else [transfer_type]
        df_all = []
        for transfer_type in transfer_type_args:
            df = await self.get_by_property(properties, transfer_type=transfer_type,ownership_type=ownership_type)
            self.logger.debug(f'Got {len(df)} rows for {transfer_type} BEFORE trimoutput, address: {address}')
            df = self.trim_output(df=df, db=db, transfer_type=transfer_type, request_cols=request_cols)
            self.logger.debug(f'Got {len(df)} rows for {transfer_type} AFTER trimoutput, address: {address}')
            df_all.append(df)

        return pd.concat(df_all)

    def trim_output(self,df : pd.DataFrame,db : pd.DataFrame,transfer_type : Literal["active","historical"],request_cols : list = None , ) -> pd.DataFrame:
        """
        Trims and merges the output DataFrame with the original property DataFrame,
        cleans up unnecessary columns, and adds metadata.

        Args:
            df (pd.DataFrame): The DataFrame containing transfer information fetched from the API.
            db (pd.DataFrame): The original DataFrame containing property identifiers
                               (e.g., kommunenummer, gaardsnummer).
            transfer_type (Literal["active", "historical"]): Indicates whether the transfers
                                                             are active or historical.
            request_cols (list, optional): A list of column names used for merging and
                                           identifying properties. Defaults to None.
        Returns:
            pd.DataFrame: The trimmed and merged DataFrame with additional metadata.
        """
        for col in request_cols:
            if df[col].dtype != db[col].dtype:
                self.logger.warning(
                    f'Column {col} has different data types in db and df. `df` has dtype {df[col].dtype} and `db` has dtype {db[col].dtype}. Forcing both to int')
                df[col] = df[col].astype(int)
                db[col] = db[col].astype(int)
        m = pd.merge(df, db.reset_index(), on=request_cols, how="left")
        view = m.drop(columns=['omsetning_oppdateringsdato_timestamp',
                               'omsetning_dokumentavgift_beloepstekst',
                               'omsetning_omsatteregisterenhetsretter_item',
                               'omsetning_avsluttetav',
                               'anmerketavids_materialised',
                               'tekster',
                               'omsetning_omsetningstypeid_value',
                               'aarsakgebyrfritakid_value',
                               'omsetning_vederlag_valutakodeid',
                               'oppdatertav',
                               'sluttdato',
                               'endretavids_materialised',
                               'omsetning_sluttdato',
                               'anmerketavids_cachedvalue_item',
                               'oppdateringsdato_timestamp',
                               'heftelseiannenrettids_materialised',
                               'omsetning_dokumentavgift_valutakodeid',
                               'endretavids_cachedvalue_item',
                               'tekster_item',
                               'omsetning_dokumentavgiftsaarsakid_value',
                               'omsetning_dokumentavgiftsgrunnlag_beloepstekst',
                               'omsetning_vederlag_beloepstekst',
                               'avsluttetav',
                               'omsetning_dokumentavgiftsgrunnlag_valutakodeid',
                               'heftelseiannenrettids_cachedvalue_item'],
                      errors="ignore")

        view.drop(columns=request_cols, inplace=True)
        view["active"] = transfer_type == "active"
        view["get_date"] = pd.Timestamp.now()
        return view
    def transform_coop(self,df: pd.DataFrame, request_cols : list = None) -> pd.DataFrame:
        '''
        Transforms a DataFrame containing cooperative property information.

        This function renames columns, handles missing values, converts data types,
        and removes duplicates to prepare the data for further processing or storage.

        Args:
            df (pd.DataFrame): The input DataFrame containing cooperative property data.
            request_cols (list): A list of column names that are expected to be numeric
                                 and are used for identifying unique cooperative units.

        Returns:
            pd.DataFrame: The transformed DataFrame.
        '''
        # df = df.copy()
        if not request_cols:
            request_cols = ["borettslagnummer", "andelsnummer"]

        rename = {"coop_org_num": "borettslagnummer",
                  "coop_unit_num": "andelsnummer",
                  }
        df.rename(columns=rename, inplace=True)
        if "item_id" in df.columns:
            df.set_index("item_id", inplace=True)
        else:
            self.logger.warning(f'item_id not found in df')
        df.dropna(subset=["borettslagnummer", "andelsnummer", ], inplace=True)
        # if "price" in df.columns:
        #     df.dropna(subset=["price"], inplace=True)
        df["andelsnummer"] = df["andelsnummer"].fillna(0)

        for col in request_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                #self.logger.warning(f'Column {col} not found in df')
                raise ValueError(f'Column {col} not found in df. Columns are {df.columns}')
        df.dropna(subset=request_cols, inplace=True)
        for col in request_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)
            else:
                self.logger.warning(f'Column {col} not found in df')
        # if "scrape_date" in df.columns:
        #     df["scrape_date"] = pd.to_datetime(df["scrape_date"])
        #     df.sort_values(by=["scrape_date"], inplace=True, ascending=False)
        df.drop_duplicates(subset=request_cols, keep="first", inplace=True)
        return df[request_cols]

    def transform_cadastrals(self,df: pd.DataFrame, request_cols : list = None) -> pd.DataFrame:
        """
        Transforms a DataFrame containing cadastral property information.

        This function renames columns, handles missing values, converts data types,
        and removes duplicates to prepare the data for further processing or storage.

        Args:
            df (pd.DataFrame): The input DataFrame containing cadastral property data.
            request_cols (list): A list of column names that are expected to be numeric
                                 and are used for identifying unique properties.
        Returns:
            pd.DataFrame: The transformed DataFrame.
        """
        # df = df.copy()
        if not request_cols:
            request_cols = ["kommunenummer", "gaardsnummer", "bruksnummer", "festenummer", "seksjonsnummer"]

        rename = {"municipality_num": "kommunenummer",
                  "cadastral_num": "gaardsnummer",
                  "unit_num": "bruksnummer",
                  "leasehold_num": "festenummer",
                  "section_num": "seksjonsnummer"}
        df.rename(columns=rename, inplace=True)
        if "item_id" in df.columns:
            df.set_index("item_id", inplace=True)
        else:
            self.logger.warning(f'item_id not found in df')

        df.dropna(subset=["gaardsnummer", "bruksnummer", ], inplace=True)
        for col in ["festenummer", "seksjonsnummer"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)
            else:
                df[col] = 0
        df = df.loc[df["gaardsnummer"] != 0, :]

        for col in request_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
                # df.loc[:, col] = pd.to_numeric(df[col], errors="coerce")
            else:
                self.logger.warning(f'Column {col} not found in df')
                if col not in ["festenummer", "seksjonsnummer"]:
                    raise ValueError(f'Required column {col} not found in df. Columns are {df.columns}')
        df.dropna(subset=request_cols, inplace=True)
        for col in request_cols:
            if col in df.columns:
                # df.loc[:,col] = df[col].astype(int)
                df[col] = df[col].astype(int)
                if col == "kommunenummer":
                    # df.loc[:, col] = df[col].apply(lambda x: str(x).zfill(4))
                    df[col] = df[col].apply(lambda x: str(x).zfill(4))
            else:
                self.logger.warning(f'Column {col} not found in df')
        df = df.loc[df["kommunenummer"] != "0000", :]
        # if "scrape_date" in df.columns:
        #     df["scrape_date"] = pd.to_datetime(df["scrape_date"])
        #     df.sort_values(by=["scrape_date"], inplace=True, ascending=False)
        df.drop_duplicates(subset=request_cols, keep="first", inplace=True)
        return df[request_cols]
