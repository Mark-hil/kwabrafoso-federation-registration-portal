from django.core.management.base import BaseCommand
from members.models import Room

class Command(BaseCommand):
    help = 'Populate the database with initial room names'

    def handle(self, *args, **options):
        # List of constellation and star names
        initial_names = [
            'Andromeda', 'Antlia', 'Apus', 'Aquarius', 'Aquila', 'Ara', 'Aries', 'Auriga',
            'Boötes', 'Caelum', 'Camelopardalis', 'Cancer', 'Canes Venatici', 'Canis Major',
            'Capricornus', 'Carina', 'Cassiopeia', 'Centaurus', 'Cepheus', 'Cetus',
            'Chamaeleon', 'Circinus', 'Columba', 'Coma Berenices', 'Corona Australis',
            'Corona Borealis', 'Corvus', 'Crater', 'Crux', 'Cygnus', 'Delphinus', 'Dorado',
            'Draco', 'Equuleus', 'Eridanus', 'Fornax', 'Gemini', 'Grus', 'Hercules',
            'Horologium', 'Hydra', 'Hydrus', 'Indus', 'Lacerta', 'Leo', 'Leo Minor',
            'Lepus', 'Libra', 'Lupus', 'Lynx', 'Lyra', 'Mensa', 'Microscopium', 'Monoceros',
            'Musca', 'Norma', 'Octans', 'Ophiuchus', 'Orion', 'Pavo', 'Pegasus', 'Perseus',
            'Phoenix', 'Pictor', 'Pisces', 'Piscis Austrinus', 'Puppis', 'Pyxis', 'Reticulum',
            'Sagitta', 'Sagittarius', 'Scorpius', 'Sculptor', 'Scutum', 'Serpens', 'Sextans',
            'Taurus', 'Telescopium', 'Triangulum', 'Triangulum Australe', 'Tucana', 'Ursa Major',
            'Ursa Minor', 'Vela', 'Virgo', 'Volans', 'Vulpecula', 'Sirius', 'Canopus', 
            'Alpha Centauri', 'Arcturus', 'Vega', 'Capella', 'Rigel', 'Procyon', 'Achernar', 
            'Betelgeuse', 'Hadar', 'Altair', 'Acrux', 'Aldebaran', 'Antares', 'Spica', 'Pollux', 
            'Fomalhaut', 'Deneb', 'Mimosa', 'Regulus', 'Adhara', 'Castor', 'Gacrux', 'Bellatrix', 
            'Elnath', 'Miaplacidus', 'Alnilam', 'Alnitak', 'Alhena', 'Polaris', 'Algol', 'Mira', 
            'Mizar', 'Alcor', 'Alcyone', 'Pleione', 'Atlas', 'Electra', 'Maia', 'Merope', 
            'Taygeta', 'Celaeno', 'Asterope', 'Almach', 'Mirach', 'Alpheratz', 'Hamal', 'Diphda', 
            'Menkar', 'Algiedi', 'Dabih', 'Nashira', 'Deneb Algedi', 'Schedar', 'Caph', 'Ruchbah', 
            'Segin', 'Achird', 'Sheratan', 'Mesarthim', 'Botein', 'Zaurak', 'Zibal', 'Azha', 
            'Acamar', 'Phact', 'Wazn', 'Mintaka', 'Saiph', 'Meissa', 'Aludra', 'Wezen', 'Furud', 
            'Mirzam', 'Tejat', 'Mebsuta', 'Mekbuda', 'Wasat'
        ]

        created_count = 0
        for name in initial_names:
            _, created = Room.objects.get_or_create(name=name)
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} rooms'))
